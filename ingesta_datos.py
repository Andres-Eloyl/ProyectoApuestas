import pandas as pd
import requests
import sqlite3
import logging
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

DB_FILE = "apuestas.db"

# Mapeo de ligas a códigos de football-data.co.uk
# Incorporaremos: EPL (E0), La Liga (SP1), Serie A (I1), Bundesliga (D1), Ligue 1 (F1)
LIGAS_TOP_5 = {
    "Premier League": "E0",
    "La Liga": "SP1",
    "Serie A": "I1",
    "Bundesliga": "D1",
    "Ligue 1": "F1",
}


def inicializar_db() -> None:
    """
    Crea las tablas en SQLite si no existen.

    ¿Por qué SQLite y no Pandas/CSV en Memoria?
    Antes cargábamos miles de filas CSV a RAM, lo que causaba cuellos de botella
    al procesar las 5 grandes ligas + Champions. SQLite permite que el motor
    inteligente lea los datos estructurados desde el disco casi al instante,
    sin colapsos de memoria.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Dropear para asegurar esquema correcto
    cursor.execute("DROP TABLE IF EXISTS historico_partidos")

    # Tabla principal de histórico de partidos jugados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "Liga" TEXT,
            "Div" TEXT,
            "Date" TEXT,
            "HomeTeam" TEXT,
            "AwayTeam" TEXT,
            "FTHG" INTEGER,
            "FTAG" INTEGER,
            "FTR" TEXT,
            "HS" INTEGER DEFAULT 0,
            "AS" INTEGER DEFAULT 0,
            "HST" INTEGER DEFAULT 0,
            "AST" INTEGER DEFAULT 0,
            "B365H" REAL DEFAULT 0.0,
            "B365D" REAL DEFAULT 0.0,
            "B365A" REAL DEFAULT 0.0,
            "Temporada" TEXT,
            UNIQUE("Date", "HomeTeam", "AwayTeam")
        )
    """)

    # Tabla de fixtures para partidos futuros (Live)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixture_hoy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Liga TEXT,
            Date TEXT,
            HomeTeam TEXT,
            AwayTeam TEXT,
            Cuota_Local REAL,
            UNIQUE(Date, HomeTeam, AwayTeam)
        )
    """)

    conn.commit()
    conn.close()
    logging.info("Base de datos local inicializada/verificada correctamente.")


def normalizar_nombres(nombre: str) -> str:
    """Normaliza nombres de equipos comunes que difieren entre orígenes."""
    mapeo = {
        "Man United": "Manchester United",
        "Man City": "Manchester City",
        "Nott'm Forest": "Nottingham Forest",
        "Ath Madrid": "Atletico Madrid",
        "Real Madrid": "Real Madrid",
        "Barcelona": "Barcelona",
        "Paris SG": "PSG",
        "Bayern Munich": "Bayern Munchen",
    }
    return mapeo.get(nombre, nombre)


def descargar_historico_top5() -> None:
    """Se conecta a los repositorios públicos de stats y descarga silenciosamente el histórico de 5 años."""
    conn = sqlite3.connect(DB_FILE)

    temporadas_str = ["2324", "2223", "2122", "2021", "1920"]  # Top 5 años recientes

    columnas_clave = [
        "Div",
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR",
        "HS",
        "AS",
        "HST",
        "AST",
        "B365H",
        "B365D",
        "B365A",
    ]

    registros_insertados = 0

    # Iteramos por cada una de las grandes ligas europeas
    for nombre_liga, codigo_liga in LIGAS_TOP_5.items():
        # Por cada liga, viajamos hasta 5 años en el pasado para construir el dataset de entrenamiento
        for temp in temporadas_str:
            url = f"https://www.football-data.co.uk/mmz4281/{temp}/{codigo_liga}.csv"

            try:
                # Descargamos directamente a DataFrame en Memoria, para luego volcarlo a SQLite
                df = pd.read_csv(url, encoding="ISO-8859-1", on_bad_lines="skip")

                # Filtrar solo columnas importantes para no saturar
                columnas_existentes = [
                    col for col in columnas_clave if col in df.columns
                ]
                df = df[columnas_existentes]

                if df.empty:
                    continue

                df["Liga"] = nombre_liga
                df["Temporada"] = temp
                df["HomeTeam"] = df["HomeTeam"].apply(normalizar_nombres)
                df["AwayTeam"] = df["AwayTeam"].apply(normalizar_nombres)

                # Dropear inconsistencias (solo base fundamental)
                df = df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"])

                # Enviar a SQLite
                for _, row in df.iterrows():
                    try:
                        conn.execute(
                            """
                            INSERT OR IGNORE INTO historico_partidos 
                            ("Liga", "Div", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", 
                             "HS", "AS", "HST", "AST", "B365H", "B365D", "B365A", "Temporada")
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                row["Liga"],
                                row.get("Div", codigo_liga),
                                str(row["Date"]),
                                row["HomeTeam"],
                                row["AwayTeam"],
                                int(row["FTHG"]),
                                int(row["FTAG"]),
                                row.get("FTR", ""),
                                int(
                                    row.get("HS", 0) if pd.notnull(row.get("HS")) else 0
                                ),
                                int(
                                    row.get("AS", 0) if pd.notnull(row.get("AS")) else 0
                                ),
                                int(
                                    row.get("HST", 0)
                                    if pd.notnull(row.get("HST"))
                                    else 0
                                ),
                                int(
                                    row.get("AST", 0)
                                    if pd.notnull(row.get("AST"))
                                    else 0
                                ),
                                float(
                                    row.get("B365H", 0.0)
                                    if pd.notnull(row.get("B365H"))
                                    else 0.0
                                ),
                                float(
                                    row.get("B365D", 0.0)
                                    if pd.notnull(row.get("B365D"))
                                    else 0.0
                                ),
                                float(
                                    row.get("B365A", 0.0)
                                    if pd.notnull(row.get("B365A"))
                                    else 0.0
                                ),
                                row["Temporada"],
                            ),
                        )
                        registros_insertados += conn.execute(
                            "SELECT changes()"
                        ).fetchone()[0]
                    except Exception as e:
                        logging.warning(
                            f"Error procesando fila de {nombre_liga} {temp}: {e}"
                        )

            except Exception as e:
                logging.warning(
                    f"No se pudo descargar {nombre_liga} Temporada {temp} de football-data: {e}"
                )

            time.sleep(1)  # Prevent rate limiting

    conn.commit()
    conn.close()


def extraer_champions_y_copas() -> None:
    """
    Scraper preventivo para extraer resultados de torneos nocaut (Champions/Copas Locales).

    Nota Técnica: Origen de Datos Alternativo
    Originalmente usamos web scraping directo con requests sobre FBref.com, pero este portal implementó
    Cloudflare HCaptcha (Escudo Anti-Bots nivel militar).
    Para no pagar proxies residenciales, extraemos los partidos directamente desde un servidor público
    CSV de fixturedownload, garantizando resiliencia, gratuidad y cero bloqueos.
    """
    conn = sqlite3.connect(DB_FILE)

    url_ucl_csv = "https://fixturedownload.com/download/champions-league-2023-UTC.csv"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        logging.info(
            "Iniciando extracción de Champions League y Copas (Origen CSV alternativo anti-bloqueo)..."
        )
        response = requests.get(url_ucl_csv, headers=headers, timeout=20)

        if response.status_code == 200:
            import io

            csv_io = io.StringIO(response.text)
            df = pd.read_csv(csv_io)

            # Formato de FixtureDownload: Match Number, Round Number, Date, Location, Home Team, Away Team, Result
            if (
                "Home Team" in df.columns
                and "Away Team" in df.columns
                and "Result" in df.columns
            ):
                df = df.dropna(subset=["Home Team", "Away Team", "Result"])
                # Solo terminados
                df = df[df["Result"].astype(str).str.contains("-", na=False)]

                registros = 0
                for _, row in df.iterrows():
                    home = normalizar_nombres(str(row["Home Team"]))
                    away = normalizar_nombres(str(row["Away Team"]))
                    score_text = str(row["Result"]).replace(" ", "")

                    try:
                        parts = score_text.split("-")
                        if len(parts) == 2:
                            fthg = int(parts[0])
                            ftag = int(parts[1])

                            if fthg > ftag:
                                ftr = "H"
                            elif ftag > fthg:
                                ftr = "A"
                            else:
                                ftr = "D"

                            date_str = str(row.get("Date", ""))
                            # Convertir fecha si es necesario a un string simple
                            date = date_str.split(" ")[0] if date_str else "2024-01-01"

                            conn.execute(
                                """
                                INSERT OR IGNORE INTO historico_partidos 
                                ("Liga", "Div", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "Temporada")
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    "Champions League",
                                    "UCL",
                                    date,
                                    home,
                                    away,
                                    fthg,
                                    ftag,
                                    ftr,
                                    "2324",
                                ),
                            )
                            registros += conn.execute("SELECT changes()").fetchone()[0]
                    except Exception:
                        continue

                logging.info(
                    f"Éxito: {registros} partidos de Champions League insertados en DB desde nuevo origen."
                )
        else:
            logging.warning(
                f"No se pudo descargar el CSV de UCL (Http {response.status_code})"
            )
    except Exception as e:
        logging.error(f"Error parseando CSV de Champions: {e}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    logging.info("Iniciando Motor Ingestor ETL (Extracción y Carga Autónoma)...")
    inicializar_db()
    descargar_historico_top5()
    time.sleep(2)  # Pausa amigable anti-bloqueo
    extraer_champions_y_copas()
