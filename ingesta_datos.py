import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def descargar_y_limpiar_datos():
    """
    Descarga los datos de las temporadas 24/25 y 25/26 (actual),
    las combina y realiza una limpieza profunda.
    """
    urls = [
        "https://www.football-data.co.uk/mmz4281/2425/SP1.csv", 
        "https://www.football-data.co.uk/mmz4281/2526/SP1.csv"  
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

    df_total = pd.concat(datasets, ignore_index=True)
    logging.info(f"Total de partidos brutos: {len(df_total)}")

    columnas_clave = [
        'Date', 'HomeTeam', 'AwayTeam', 
        'FTHG', 'FTAG', 'FTR', 
        'B365H', 'B365D', 'B365A'
    ]
    
    df_limpio = df_total[columnas_clave].copy()

    df_limpio = df_limpio.dropna()


    df_limpio['Date'] = pd.to_datetime(df_limpio['Date'], dayfirst=True, errors='coerce')
    df_limpio = df_limpio.dropna(subset=['Date']) 
    

    df_limpio = df_limpio.sort_values(by='Date')


    df_limpio.to_csv('partidos_procesados.csv', index=False)
    logging.info(f"Ingesta completada. Archivo 'partidos_procesados.csv' guardado con {len(df_limpio)} filas.")

if __name__ == "__main__":
    descargar_y_limpiar_datos()