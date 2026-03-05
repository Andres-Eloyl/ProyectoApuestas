import pandas as pd
import requests
import logging
import os
import json
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

API_KEY = os.environ.get("ODDS_API_KEY")

# Extraemos las Top 5 ligas de Europa + Champions League interconectando con TheOdds API
# Usamos las 'keys' exactas que provee la documentación de The Odds API
SPORTS = [
    "soccer_spain_la_liga",
    "soccer_epl",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga",
    "soccer_france_ligue_one",
    "soccer_uefa_champs_league"
]

REGIONS = "eu"
MARKETS = "h2h"

# Mapeo vital: 'TheOddsAPI' y 'Football-Data' nombran a los equipos distinto.
# Por ejemplo, uno dice 'Athletic Club' y otro 'Ath Bilbao'. Este traductor 
# estandariza los nombres para poder cruzar cuotas con estadísticas históricas.
TRADUCTOR = {
    "Athletic Club": "Ath Bilbao", "Athletic Bilbao": "Ath Bilbao", 
    "Real Betis": "Betis", "Real Sociedad": "Sociedad", "Real Oviedo": "Oviedo",
    "Real Madrid": "Real Madrid", "FC Barcelona": "Barcelona",
    "Atletico Madrid": "Ath Madrid", "Atlético Madrid": "Ath Madrid", 
    "CA Osasuna": "Osasuna", "Celta Vigo": "Celta", "Alavés": "Alaves",
    "Levante": "Levante", "Rayo Vallecano": "Vallecano",
    "Elche CF": "Elche", "Girona": "Girona", "Mallorca": "Mallorca",
    "Valencia": "Valencia", "Manchester City": "Man City", "Manchester United": "Man United",
    "Newcastle United": "Newcastle", "Tottenham Hotspur": "Tottenham", "Aston Villa": "Aston Villa",
    "West Ham United": "West Ham", "Brighton & Hove Albion": "Brighton", "Wolverhampton Wanderers": "Wolves",
    "Nottingham Forest": "Nott'm Forest", "Sheffield United": "Sheffield United",
    "Bayern Munich": "Bayern Munich", "Borussia Dortmund": "Dortmund",
    "Bayer Leverkusen": "Leverkusen", "RB Leipzig": "RB Leipzig", "Eintracht Frankfurt": "Ein Frankfurt",
    "Paris Saint Germain": "PSG", "Olympique Marseille": "Marseille", "Olympique Lyonnais": "Lyon",
    "Inter Milan": "Inter", "AC Milan": "Milan", "Juventus": "Juventus", "Roma": "Roma", "Napoli": "Napoli"
}

def generar_cartelera_diaria():
    # 1. Cargamos el caché de estadísticas (stats_actuales.json)
    # Hacer esto vía JSON es 10x más rápido que consultar la BD SQL partido por partido
    logging.info("1. Cargando estadísticas neuronales desde stats_actuales.json...")
    
    try:
        with open('stats_actuales.json', 'r') as f:
            stats_historicas = json.load(f)
    except FileNotFoundError:
        logging.error("❌ No existe stats_actuales.json. Debes ejecutar ingenieria_caracteristicas.py primero.")
        return

    from datetime import timedelta
        
    partidos_hoy = []
    # Adelantamos el reloj para tener las predicciones 1 día antes
    hoy = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y-%m-%d')
    
    logging.info(f"2. Escaneando la cartelera de Europa para MAÑANA ({hoy})...")
    
    # Flag para saber si usamos mock
    usar_mock = False

    # Recorremos cada una de las grandes ligas buscando si hay partidos programados hoy
    for sport in SPORTS:
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}"
        
        try:
            if API_KEY is None or API_KEY == "TU_API_KEY":
                usar_mock = True
                break
                
            respuesta = requests.get(url)
            if respuesta.status_code == 401:
                logging.warning(f"Error 401: Clave API({API_KEY}) de TheOdds invalida o ausente.")
                usar_mock = True
                break
                
            datos_api = respuesta.json()
            if not isinstance(datos_api, list):
                continue
                
            for partido in datos_api:
                if not partido['commence_time'].startswith(hoy):
                    continue
                    
                eq_local_api = partido['home_team']
                eq_visita_api = partido['away_team']
                
                eq_l = TRADUCTOR.get(eq_local_api, eq_local_api)
                eq_v = TRADUCTOR.get(eq_visita_api, eq_visita_api)
                
                if eq_l not in stats_historicas or eq_v not in stats_historicas:
                    # En competiciones como la champions puede haber equipos fuera de los top5 (ej. Estrella roja)
                    logging.debug(f"Saltando {eq_l} vs {eq_v} - Ausente en la BD de historia.")
                    continue
                
                # Cargar el vector mágico de xG
                stats_l = stats_historicas[eq_l]
                stats_v = stats_historicas[eq_v]
                
                try:
                    mercados = partido['bookmakers'][0]['markets'][0]['outcomes']
                    cuota_h = next(c['price'] for c in mercados if c['name'] == eq_local_api)
                    cuota_d = next(c['price'] for c in mercados if c['name'] == 'Draw')
                    cuota_a = next(c['price'] for c in mercados if c['name'] == eq_visita_api)
                except Exception:
                    continue # Sin cuotas
                    
                partidos_hoy.append({
                    'HomeTeam': eq_l,
                    'AwayTeam': eq_v,
                    'Racha_Local': stats_l['Racha'],
                    'Racha_Visita': stats_v['Racha'],
                    'Dif_Goles_Local': stats_l['Dif_Goles'],
                    'Dif_Goles_Visita': stats_v['Dif_Goles'],
                    'xG_Favor_Local': stats_l['xG_Favor'],
                    'xG_Contra_Local': stats_l['xG_Contra'],
                    'xG_Favor_Visita': stats_v['xG_Favor'],
                    'xG_Contra_Visita': stats_v['xG_Contra'],
                    'Pts_Totales_Local': stats_l['Pts_Totales'],
                    'Pts_Totales_Visita': stats_v['Pts_Totales'],
                    'B365H': cuota_h,
                    'B365D': cuota_d,
                    'B365A': cuota_a
                })
            if usar_mock:
                break
                
        except Exception as e:
            logging.error(f"Error parseando la liga {sport}: {e}")
            
    if usar_mock:
        logging.info("⭐ Modo Simulador Activado (Falta Clave API real). Insertando partidos Top 5 destacados de prueba...")
        # Generamos partidos simulados super realistas basados en los datos historicos reales
        partidos_hoy = [
            {
                'HomeTeam': 'Ath Madrid', 'AwayTeam': 'Barcelona',
                'Racha_Local': stats_historicas.get('Ath Madrid', {}).get('Racha', 6),
                'Racha_Visita': stats_historicas.get('Barcelona', {}).get('Racha', 7),
                'Dif_Goles_Local': stats_historicas.get('Ath Madrid', {}).get('Dif_Goles', 10),
                'Dif_Goles_Visita': stats_historicas.get('Barcelona', {}).get('Dif_Goles', 25),
                'xG_Favor_Local': stats_historicas.get('Ath Madrid', {}).get('xG_Favor', 1.8),
                'xG_Contra_Local': stats_historicas.get('Ath Madrid', {}).get('xG_Contra', 0.9),
                'xG_Favor_Visita': stats_historicas.get('Barcelona', {}).get('xG_Favor', 2.5),
                'xG_Contra_Visita': stats_historicas.get('Barcelona', {}).get('xG_Contra', 1.1),
                'Pts_Totales_Local': stats_historicas.get('Ath Madrid', {}).get('Pts_Totales', 60),
                'Pts_Totales_Visita': stats_historicas.get('Barcelona', {}).get('Pts_Totales', 75),
                'B365H': 2.80, 'B365D': 3.40, 'B365A': 2.45
            },
            {
                'HomeTeam': 'Bayern Munich', 'AwayTeam': 'Dortmund',
                'Racha_Local': stats_historicas.get('Bayern Munich', {}).get('Racha', 9),
                'Racha_Visita': stats_historicas.get('Dortmund', {}).get('Racha', 5),
                'Dif_Goles_Local': stats_historicas.get('Bayern Munich', {}).get('Dif_Goles', 35),
                'Dif_Goles_Visita': stats_historicas.get('Dortmund', {}).get('Dif_Goles', 15),
                'xG_Favor_Local': stats_historicas.get('Bayern Munich', {}).get('xG_Favor', 2.9),
                'xG_Contra_Local': stats_historicas.get('Bayern Munich', {}).get('xG_Contra', 1.0),
                'xG_Favor_Visita': stats_historicas.get('Dortmund', {}).get('xG_Favor', 1.6),
                'xG_Contra_Visita': stats_historicas.get('Dortmund', {}).get('xG_Contra', 1.4),
                'Pts_Totales_Local': stats_historicas.get('Bayern Munich', {}).get('Pts_Totales', 70),
                'Pts_Totales_Visita': stats_historicas.get('Dortmund', {}).get('Pts_Totales', 55),
                'B365H': 1.60, 'B365D': 4.50, 'B365A': 5.00
            },
            {
                'HomeTeam': 'PSG', 'AwayTeam': 'Marseille',
                'Racha_Local': stats_historicas.get('PSG', {}).get('Racha', 7),
                'Racha_Visita': stats_historicas.get('Marseille', {}).get('Racha', 4),
                'Dif_Goles_Local': stats_historicas.get('PSG', {}).get('Dif_Goles', 22),
                'Dif_Goles_Visita': stats_historicas.get('Marseille', {}).get('Dif_Goles', 8),
                'xG_Favor_Local': stats_historicas.get('PSG', {}).get('xG_Favor', 2.3),
                'xG_Contra_Local': stats_historicas.get('PSG', {}).get('xG_Contra', 0.8),
                'xG_Favor_Visita': stats_historicas.get('Marseille', {}).get('xG_Favor', 1.4),
                'xG_Contra_Visita': stats_historicas.get('Marseille', {}).get('xG_Contra', 1.2),
                'Pts_Totales_Local': stats_historicas.get('PSG', {}).get('Pts_Totales', 65),
                'Pts_Totales_Visita': stats_historicas.get('Marseille', {}).get('Pts_Totales', 50),
                'B365H': 1.45, 'B365D': 4.80, 'B365A': 6.50
            },
            {
                'HomeTeam': 'Man City', 'AwayTeam': 'Arsenal',
                'Racha_Local': stats_historicas.get('Man City', {}).get('Racha', 9),
                'Racha_Visita': stats_historicas.get('Arsenal', {}).get('Racha', 7),
                'Dif_Goles_Local': stats_historicas.get('Man City', {}).get('Dif_Goles', 30),
                'Dif_Goles_Visita': stats_historicas.get('Arsenal', {}).get('Dif_Goles', 25),
                'xG_Favor_Local': stats_historicas.get('Man City', {}).get('xG_Favor', 2.8),
                'xG_Contra_Local': stats_historicas.get('Man City', {}).get('xG_Contra', 0.9),
                'xG_Favor_Visita': stats_historicas.get('Arsenal', {}).get('xG_Favor', 2.4),
                'xG_Contra_Visita': stats_historicas.get('Arsenal', {}).get('xG_Contra', 1.0),
                'Pts_Totales_Local': stats_historicas.get('Man City', {}).get('Pts_Totales', 72),
                'Pts_Totales_Visita': stats_historicas.get('Arsenal', {}).get('Pts_Totales', 68),
                'B365H': 2.10, 'B365D': 3.50, 'B365A': 3.20
            },
            {
                'HomeTeam': 'Juventus', 'AwayTeam': 'Inter',
                'Racha_Local': stats_historicas.get('Juventus', {}).get('Racha', 8),
                'Racha_Visita': stats_historicas.get('Inter', {}).get('Racha', 9),
                'Dif_Goles_Local': stats_historicas.get('Juventus', {}).get('Dif_Goles', 18),
                'Dif_Goles_Visita': stats_historicas.get('Inter', {}).get('Dif_Goles', 24),
                'xG_Favor_Local': stats_historicas.get('Juventus', {}).get('xG_Favor', 1.6),
                'xG_Contra_Local': stats_historicas.get('Juventus', {}).get('xG_Contra', 0.6),
                'xG_Favor_Visita': stats_historicas.get('Inter', {}).get('xG_Favor', 2.1),
                'xG_Contra_Visita': stats_historicas.get('Inter', {}).get('xG_Contra', 0.8),
                'Pts_Totales_Local': stats_historicas.get('Juventus', {}).get('Pts_Totales', 60),
                'Pts_Totales_Visita': stats_historicas.get('Inter', {}).get('Pts_Totales', 69),
                'B365H': 2.80, 'B365D': 3.10, 'B365A': 2.60
            }
        ]
            
    if partidos_hoy:
        df_hoy = pd.DataFrame(partidos_hoy)
        df_hoy.to_csv('partidos_hoy.csv', index=False)
        logging.info(f"✅ ¡Éxito! Cartelera lista: {len(df_hoy)} partidos en CSV ('partidos_hoy.csv').")
    else:
        logging.warning("⚠️ No se encontraron partidos para el día de hoy con estadísticas completas o la API KeyError.")

if __name__ == '__main__':
    generar_cartelera_diaria()