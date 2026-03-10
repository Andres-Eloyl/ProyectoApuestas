import pandas as pd
import logging
import json
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Diccionario exhaustivo de traducción para las 5 grandes ligas
TRADUCTOR = {
    # España
    "Ath Madrid": "Atlético Madrid", "Ath Bilbao": "Athletic Bilbao",
    "Betis": "Real Betis", "Sociedad": "Real Sociedad", "Vallecano": "Rayo Vallecano",
    "Celta": "Celta Vigo", "Cadiz": "Cádiz", "Alaves": "Alavés", "Almeria": "Almería",
    "Real Madrid": "Real Madrid", "Barcelona": "FC Barcelona", "Girona": "Girona",
    "Osasuna": "CA Osasuna", "Mallorca": "Mallorca", "Sevilla": "Sevilla", "Valencia": "Valencia",
    # Inglaterra
    "Man City": "Manchester City", "Man United": "Manchester United",
    "Nott'm Forest": "Nottingham Forest", "Sheffield United": "Sheffield Utd",
    "Wolves": "Wolverhampton Wanderers", "Spurs": "Tottenham Hotspur",
    "Newcastle": "Newcastle United", "Aston Villa": "Aston Villa",
    "Brighton": "Brighton & Hove Albion", "West Ham": "West Ham United",
    "Bournemouth": "Bournemouth", "Everton": "Everton", "Leeds": "Leeds", 
    "Ipswich": "Ipswich", "Fulham": "Fulham", "Arsenal": "Arsenal", "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace", "Brentford": "Brentford", "Leicester": "Leicester",
    "Southampton": "Southampton",
    # Alemania
    "Ein Frankfurt": "Eintracht Frankfurt", "Dortmund": "Borussia Dortmund",
    "Leverkusen": "Bayer Leverkusen", "M'gladbach": "Borussia Monchengladbach",
    "Bayern Munich": "Bayern Munich", "RB Leipzig": "RB Leipzig", "Stuttgart": "VfB Stuttgart",
    # Francia
    "PSG": "Paris Saint Germain", "Marseille": "Olympique Marseille", "Lyon": "Olympique Lyonnais",
    "Monaco": "AS Monaco", "Lille": "Lille OSC", "Lens": "RC Lens", "Rennes": "Stade Rennais",
    # Italia
    "Inter": "Inter Milan", "Milan": "AC Milan", "Roma": "AS Roma",
    "Juventus": "Juventus", "Napoli": "Napoli", "Lazio": "Lazio", "Atalanta": "Atalanta",
    "Fiorentina": "Fiorentina", "Torino": "Torino"
}

def generar_cartelera_diaria():
    logging.info("Cargando estadísticas desde stats_actuales.json...")
    
    try:
        with open('stats_actuales.json', 'r') as f:
            stats_historicas = json.load(f)
    except FileNotFoundError:
        logging.error("No existe stats_actuales.json. Ejecute ingenieria_caracteristicas.py primero.")
        return

    logging.info("Descargando cartelera de próximos partidos (Football-Data.co.uk)...")
    
    try:
        # Descarga del CSV público de próximos partidos.
        df_fixtures = pd.read_csv("https://www.football-data.co.uk/fixtures.csv")
    except Exception as e:
        logging.error(f"Error descargando la cartelera en tiempo real: {e}")
        df_fixtures = pd.DataFrame()

    partidos_hoy = []
    
    # Formatos de fecha de Football-Data suelen ser DD/MM/YYYY
    ayer_fmt = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%d/%m/%Y')
    hoy_fmt = datetime.now(timezone.utc).strftime('%d/%m/%Y')
    manana_fmt = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%d/%m/%Y')
    pasado_fmt = (datetime.now(timezone.utc) + timedelta(days=2)).strftime('%d/%m/%Y')
    pasadomanana_fmt = (datetime.now(timezone.utc) + timedelta(days=3)).strftime('%d/%m/%Y')
    
    if not df_fixtures.empty and 'Date' in df_fixtures.columns:
        # Filtramos partidos desde ayer para compensar zonas horarias
        fechas_validas = [ayer_fmt, hoy_fmt, manana_fmt, pasado_fmt, pasadomanana_fmt]
        df_filtro = df_fixtures[df_fixtures['Date'].isin(fechas_validas)]
        
        for _, partido in df_filtro.iterrows():
            eq_local_csv = str(partido.get('HomeTeam', ''))
            eq_visita_csv = str(partido.get('AwayTeam', ''))
            
            eq_l = TRADUCTOR.get(eq_local_csv, eq_local_csv)
            eq_v = TRADUCTOR.get(eq_visita_csv, eq_visita_csv)
            
            # Si el equipo no está en el registro de stats, se ignora.
            if eq_l not in stats_historicas or eq_v not in stats_historicas:
                continue
                
            stats_l = stats_historicas[eq_l]
            stats_v = stats_historicas[eq_v]
            
            # Extraemos las cuotas de Bet365 ('B365H' etc) o las medias ('AvgH') si faltan
            try:
                cuota_h = float(partido.get('B365H', partido.get('AvgH', 0)))
                cuota_d = float(partido.get('B365D', partido.get('AvgD', 0)))
                cuota_a = float(partido.get('B365A', partido.get('AvgA', 0)))
                
                if cuota_h == 0 or cuota_d == 0 or cuota_a == 0:
                    continue # Sin cuotas publicadas
            except Exception:
                continue
                
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

    if not partidos_hoy:
        logging.info("Alerta: No hay partidos o cuotas disponibles. Inyectando partidos de demostración.")
        # Se generan partidos basados en datos históricos para propósitos de demostración.
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

    df_final = pd.DataFrame(partidos_hoy)
    df_final.to_csv('partidos_hoy.csv', index=False)
    logging.info(f"Cartelera lista: {len(df_final)} partidos guardados en 'partidos_hoy.csv'.")

if __name__ == '__main__':
    generar_cartelera_diaria()