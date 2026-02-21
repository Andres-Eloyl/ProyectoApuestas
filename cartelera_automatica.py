import pandas as pd
import requests
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

API_KEY = os.environ.get("5749c8a9d8882209e480dba0c542e21f")
SPORT = "soccer_spain_la_liga" 
REGIONS = "eu"
MARKETS = "h2h"

TRADUCTOR = {
    "Athletic Club": "Ath Bilbao",
    "Athletic Bilbao": "Ath Bilbao", 
    "Real Betis": "Betis",
    "Real Sociedad": "Sociedad",
    "Real Oviedo": "Oviedo",
    "Real Madrid": "Real Madrid",
    "FC Barcelona": "Barcelona",
    "Atletico Madrid": "Ath Madrid",
    "Atlético Madrid": "Ath Madrid", 
    "CA Osasuna": "Osasuna",
    "Celta Vigo": "Celta",
    "Alavés": "Alaves",
    "Levante": "Levante",
    "Rayo Vallecano": "Vallecano",
    "Elche CF": "Elche",
    "Girona": "Girona",
    "Mallorca": "Mallorca",
    "Valencia": "Valencia"
}

def obtener_estado_actual_equipos(ruta_csv):
    """Recorre el historial y devuelve las estadísticas actualizadas de todos los equipos."""
    df = pd.read_csv(ruta_csv)
    stats = {}
    
    for _, fila in df.iterrows():
        local, visita = fila['HomeTeam'], fila['AwayTeam']
        resultado = fila['FTR']
        goles_l, goles_v = fila['FTHG'], fila['FTAG']

        for eq in [local, visita]:
            if eq not in stats:
                stats[eq] = {'puntos_hist': [], 'goles_f': [], 'goles_c': [], 'total_pts': 0}

        if resultado == 'H':
            stats[local]['puntos_hist'].append(3); stats[visita]['puntos_hist'].append(0)
            stats[local]['total_pts'] += 3
        elif resultado == 'A':
            stats[local]['puntos_hist'].append(0); stats[visita]['puntos_hist'].append(3)
            stats[visita]['total_pts'] += 3
        else:
            stats[local]['puntos_hist'].append(1); stats[visita]['puntos_hist'].append(1)
            stats[local]['total_pts'] += 1; stats[visita]['total_pts'] += 1

        stats[local]['goles_f'].append(goles_l); stats[local]['goles_c'].append(goles_v)
        stats[visita]['goles_f'].append(goles_v); stats[visita]['goles_c'].append(goles_l)
        
    return stats

def generar_cartelera_diaria():
    logging.info("1. Calculando estadísticas actuales desde el historial...")
    try:
        stats_historicas = obtener_estado_actual_equipos('partidos_procesados.csv')
    except Exception as e:
        logging.error(f"Error leyendo historial: {e}")
        return

    logging.info("2. Descargando cuotas en vivo desde The Odds API...")
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}"
    
    try:
        datos_api = requests.get(url).json()
    except Exception as e:
        logging.error(f"Error en la API: {e}")
        return
        
    partidos_hoy = []
    
    logging.info("3. Cruzando datos y generando Machine Learning Features...")
    for partido in datos_api:
        eq_local_api = partido['home_team']
        eq_visita_api = partido['away_team']
        
        eq_l = TRADUCTOR.get(eq_local_api, eq_local_api)
        eq_v = TRADUCTOR.get(eq_visita_api, eq_visita_api)
        
        if eq_l not in stats_historicas or eq_v not in stats_historicas:
            logging.warning(f"Saltando {eq_l} vs {eq_v} - No hay historial previo.")
            continue
            
        racha_l = sum(stats_historicas[eq_l]['puntos_hist'][-3:])
        racha_v = sum(stats_historicas[eq_v]['puntos_hist'][-3:])
        dif_g_l = sum(stats_historicas[eq_l]['goles_f'][-3:]) - sum(stats_historicas[eq_l]['goles_c'][-3:])
        dif_g_v = sum(stats_historicas[eq_v]['goles_f'][-3:]) - sum(stats_historicas[eq_v]['goles_c'][-3:])
        pts_l = stats_historicas[eq_l]['total_pts']
        pts_v = stats_historicas[eq_v]['total_pts']
        
        try:
            mercados = partido['bookmakers'][0]['markets'][0]['outcomes']
            cuota_h = next(c['price'] for c in mercados if c['name'] == eq_local_api)
            cuota_d = next(c['price'] for c in mercados if c['name'] == 'Draw')
            cuota_a = next(c['price'] for c in mercados if c['name'] == eq_visita_api)
        except Exception as e:
            logging.warning(f"Saltando {eq_l} vs {eq_v} - Sin cuotas disponibles.")
            continue
            
        partidos_hoy.append({
            'HomeTeam': eq_l,
            'AwayTeam': eq_v,
            'Racha_Local': racha_l,
            'Racha_Visita': racha_v,
            'Dif_Goles_Local': dif_g_l,
            'Dif_Goles_Visita': dif_g_v,
            'Pts_Totales_Local': pts_l,
            'Pts_Totales_Visita': pts_v,
            'B365H': cuota_h,
            'B365D': cuota_d,
            'B365A': cuota_a
        })
        
    df_hoy = pd.DataFrame(partidos_hoy)
    df_hoy.to_csv('partidos_hoy.csv', index=False)
    logging.info(f"✅ ¡Éxito! Se guardó 'partidos_hoy.csv' con {len(df_hoy)} partidos listos para la IA.")

if __name__ == '__main__':
    generar_cartelera_diaria()