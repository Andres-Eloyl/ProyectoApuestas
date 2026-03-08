import pandas as pd
import logging

import sqlite3

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def generar_dataset_ml() -> None:
    """
    Lee el histórico de partidos desde SQLite y computa características avanzadas
    (Rachas, Diferencia de Goles, xG Ponderado) usando ventana iterativa.
    Genera 'dataset_final_ml.csv' para el entrenamiento y 'stats_actuales.json'.
    """
    logging.info("Iniciando ingeniería de características desde SQLite...")
    try:
        conn = sqlite3.connect("apuestas.db")
        df = pd.read_sql("SELECT * FROM historico_partidos ORDER BY Date ASC", conn)
        conn.close()
        if df.empty:
            logging.error(
                "La base de datos está vacía. Ejecuta ingesta_datos.py primero."
            )
            return
    except sqlite3.Error as e:
        logging.error(f"Error conectando a la BD: {e}")
        return

    stats = {}

    features_lista = []

    for i, fila in df.iterrows():
        local = fila["HomeTeam"]
        visita = fila["AwayTeam"]
        resultado = fila["FTR"]
        goles_l = fila["FTHG"]
        goles_v = fila["FTAG"]

        # Tiros
        hs_l = fila.get("HS", 0)
        as_v = fila.get("AS", 0)
        hst_l = fila.get("HST", 0)
        ast_v = fila.get("AST", 0)

        # xG Estimado (Modelo Naive: 0.3 por tiro a puerta, 0.05 por tiro general)
        xg_partido_l = (hst_l * 0.3) + (hs_l * 0.05)
        xg_partido_v = (ast_v * 0.3) + (as_v * 0.05)

        for equipo in [local, visita]:
            if equipo not in stats:
                stats[equipo] = {
                    "puntos_hist": [],
                    "goles_f": [],
                    "goles_c": [],
                    "total_pts": 0,
                    "xg_f": [],
                    "xg_c": [],
                }

        racha_l = sum(stats[local]["puntos_hist"][-3:])
        racha_v = sum(stats[visita]["puntos_hist"][-3:])

        dif_g_l = sum(stats[local]["goles_f"][-3:]) - sum(stats[local]["goles_c"][-3:])
        dif_g_v = sum(stats[visita]["goles_f"][-3:]) - sum(
            stats[visita]["goles_c"][-3:]
        )

        # Promedio xG últimos 3 partidos
        xg_f_l = sum(stats[local]["xg_f"][-3:]) / 3 if stats[local]["xg_f"] else 1.2
        xg_c_l = sum(stats[local]["xg_c"][-3:]) / 3 if stats[local]["xg_c"] else 1.2
        xg_f_v = sum(stats[visita]["xg_f"][-3:]) / 3 if stats[visita]["xg_f"] else 1.2
        xg_c_v = sum(stats[visita]["xg_c"][-3:]) / 3 if stats[visita]["xg_c"] else 1.2

        pts_tot_l = stats[local]["total_pts"]
        pts_tot_v = stats[visita]["total_pts"]

        features_lista.append(
            {
                "Racha_Local": racha_l,
                "Racha_Visita": racha_v,
                "Dif_Goles_Local": dif_g_l,
                "Dif_Goles_Visita": dif_g_v,
                "xG_Favor_Local": xg_f_l,
                "xG_Contra_Local": xg_c_l,
                "xG_Favor_Visita": xg_f_v,
                "xG_Contra_Visita": xg_c_v,
                "Pts_Totales_Local": pts_tot_l,
                "Pts_Totales_Visita": pts_tot_v,
                "FTR": resultado,
                "B365H": fila["B365H"],
                "B365D": fila["B365D"],
                "B365A": fila["B365A"],
            }
        )

        if resultado == "H":
            stats[local]["puntos_hist"].append(3)
            stats[visita]["puntos_hist"].append(0)
            stats[local]["total_pts"] += 3
        elif resultado == "A":
            stats[local]["puntos_hist"].append(0)
            stats[visita]["puntos_hist"].append(3)
            stats[visita]["total_pts"] += 3
        else:
            stats[local]["puntos_hist"].append(1)
            stats[visita]["puntos_hist"].append(1)
            stats[local]["total_pts"] += 1
            stats[visita]["total_pts"] += 1

        stats[local]["goles_f"].append(goles_l)
        stats[local]["goles_c"].append(goles_v)
        stats[visita]["goles_f"].append(goles_v)
        stats[visita]["goles_c"].append(goles_l)

        stats[local]["xg_f"].append(xg_partido_l)
        stats[local]["xg_c"].append(xg_partido_v)
        stats[visita]["xg_f"].append(xg_partido_v)
        stats[visita]["xg_c"].append(xg_partido_l)

    df_final = pd.DataFrame(features_lista)
    df_final.to_csv("dataset_final_ml.csv", index=False)

    # === Exportar stats actuales para predicciones en vivo ===
    import json

    stats_actuales = {}
    for equipo, data in stats.items():
        stats_actuales[equipo] = {
            "Racha": sum(data["puntos_hist"][-3:]),
            "Dif_Goles": sum(data["goles_f"][-3:]) - sum(data["goles_c"][-3:]),
            "xG_Favor": sum(data["xg_f"][-3:]) / 3 if data["xg_f"] else 1.2,
            "xG_Contra": sum(data["xg_c"][-3:]) / 3 if data["xg_c"] else 1.2,
            "Pts_Totales": data["total_pts"],
        }
    with open("stats_actuales.json", "w") as f:
        json.dump(stats_actuales, f)

    logging.info(
        f"Éxito: Se generó 'dataset_final_ml.csv' con {len(df_final)} partidos y 'stats_actuales.json'."
    )


if __name__ == "__main__":
    generar_dataset_ml()
