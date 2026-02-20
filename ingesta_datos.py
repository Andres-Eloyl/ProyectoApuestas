import pandas as pd
import logging

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def descargar_y_limpiar_datos():
    """
    Descarga los datos de las temporadas 24/25 y 25/26 (actual),
    las combina y realiza una limpieza profunda.
    """
    # URLs oficiales de la liga española (SP1)
    urls = [
        "https://www.football-data.co.uk/mmz4281/2425/SP1.csv", # Temporada pasada
        "https://www.football-data.co.uk/mmz4281/2526/SP1.csv"  # Temporada actual (Feb 2026)
    ]
    
    datasets = []
    
    for url in urls:
        try:
            logging.info(f"Descargando datos desde: {url}...")
            df = pd.read_csv(url)
            datasets.append(df)
        except Exception as e:
            logging.error(f"No se pudo descargar la URL {url}. Error: {e}")

    if not datasets:
        logging.critical("No se pudo obtener ningún dato. Abortando.")
        return

    # 1. Combinar temporadas (Concatenación)
    df_total = pd.concat(datasets, ignore_index=True)
    logging.info(f"Total de partidos brutos: {len(df_total)}")

    # 2. Selección de columnas críticas
    # FTHG: Goles Local, FTAG: Goles Visita, FTR: Resultado Final
    # B365...: Cuotas de Bet365
    columnas_clave = [
        'Date', 'HomeTeam', 'AwayTeam', 
        'FTHG', 'FTAG', 'FTR', 
        'B365H', 'B365D', 'B365A'
    ]
    
    # Nos aseguramos de que solo existan estas columnas
    df_limpio = df_total[columnas_clave].copy()

    # 3. Limpieza de filas vacías (partidos suspendidos o sin cuotas)
    df_limpio = df_limpio.dropna()

    # 4. Formateo de fechas (Crucial para el orden cronológico)
    # Algunos CSV usan formatos distintos, intentamos convertir con seguridad
    df_limpio['Date'] = pd.to_datetime(df_limpio['Date'], dayfirst=True, errors='coerce')
    df_limpio = df_limpio.dropna(subset=['Date']) # Eliminamos si la fecha es inválida
    
    # Ordenamos por fecha para que el cálculo de rachas sea correcto
    df_limpio = df_limpio.sort_values(by='Date')

    # 5. Guardar el archivo maestro
    df_limpio.to_csv('partidos_procesados.csv', index=False)
    logging.info(f"Ingesta completada. Archivo 'partidos_procesados.csv' guardado con {len(df_limpio)} filas.")

if __name__ == "__main__":
    descargar_y_limpiar_datos()