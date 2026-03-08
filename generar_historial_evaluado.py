import pandas as pd
import json
import logging
import numpy as np
from modelos_poo import PredictorGradientBoosting

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Mismo traductor exacto usado en cartelera_automatica para mantener congruencia
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
    # Italia
    "Inter": "Inter Milan", "Milan": "AC Milan", "Roma": "AS Roma",
    "Juventus": "Juventus", "Napoli": "Napoli", "Lazio": "Lazio", "Atalanta": "Atalanta",
    "Fiorentina": "Fiorentina", "Torino": "Torino"
}

SOURCES = {
    "Premier_League": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "La_Liga": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Serie_A": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Bundesliga": "https://www.football-data.co.uk/mmz4281/2526/D1.csv"
}

def generar_auditoria():
    logging.info("1. Entrenando Motor IA Principal...")
    bot = PredictorGradientBoosting(ruta_csv='dataset_final_ml.csv')
    bot.cargar_datos()
    bot.features = ['Racha_Local', 'Racha_Visita', 'Dif_Goles_Local', 
                    'Dif_Goles_Visita', 'Pts_Totales_Local', 'Pts_Totales_Visita',
                    'xG_Favor_Local', 'xG_Contra_Local', 'xG_Favor_Visita', 'xG_Contra_Visita']
    X = bot.df[bot.features]
    y = bot.df['FTR']
    bot.entrenar(X, y)
    
    clases = list(bot.obtener_clases())

    logging.info("2. Cargando Stats Actuales...")
    try:
        with open('stats_actuales.json', 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        logging.error("No se encontró stats_actuales.json. Debe existir.")
        return

    historial_final = []

    logging.info("3. Descargando Archivos CSV de la Primera Mitad de Temporada...")
    for liga, url in SOURCES.items():
        logging.info(f"   -> Procesando {liga}...")
        try:
            df = pd.read_csv(url)
            # Solo partidos jugados (tienen FTR)
            df = df.dropna(subset=['FTR'])
            
            for _, fila in df.iterrows():
                # Extracción y traducción
                home_raw = str(fila.get('HomeTeam', ''))
                away_raw = str(fila.get('AwayTeam', ''))
                
                home_t = TRADUCTOR.get(home_raw, home_raw)
                away_t = TRADUCTOR.get(away_raw, away_raw)
                
                if home_t not in stats or away_t not in stats:
                    continue
                    
                s_l = stats[home_t]
                s_v = stats[away_t]
                
                # Armamos el vector para predecir respetando el orden exacto de bot.features
                features_partido = pd.DataFrame([{
                    'Racha_Local': s_l['Racha'],
                    'Racha_Visita': s_v['Racha'],
                    'Dif_Goles_Local': s_l['Dif_Goles'],
                    'Dif_Goles_Visita': s_v['Dif_Goles'],
                    'Pts_Totales_Local': s_l['Pts_Totales'],
                    'Pts_Totales_Visita': s_v['Pts_Totales'],
                    'xG_Favor_Local': s_l['xG_Favor'],
                    'xG_Contra_Local': s_l['xG_Contra'],
                    'xG_Favor_Visita': s_v['xG_Favor'],
                    'xG_Contra_Visita': s_v['xG_Contra']
                }])
                
                probs = bot.predecir_probabilidades(features_partido)[0]
                
                # Encontrar la clase (H, D, A) con la probabilidad más alta
                prediccion_clase = clases[np.argmax(probs)]
                
                resultado_real = fila['FTR']
                acierto = "✅" if prediccion_clase == resultado_real else "❌"
                
                try:
                    cuota_local = float(fila.get('B365H', fila.get('AvgH', 0)))
                except Exception:
                    cuota_local = 0.0
                
                fecha_partido = fila.get('Date', 'N/A')
                
                historial_final.append({
                    "Liga": liga.replace("_", " "),
                    "Fecha": fecha_partido,
                    "Partido": f"{home_t} vs {away_t}",
                    "Prediccion_IA": prediccion_clase,
                    "Resultado_Real": resultado_real,
                    "Acierto": acierto,
                    "Info_Extra": f"Prob IA: H({probs[clases.index('H')]:.2f}) D({probs[clases.index('D')]:.2f}) A({probs[clases.index('A')]:.2f}) | Cuota: {cuota_local}"
                })
                
        except Exception as e:
            logging.error(f"Error parseando {liga}: {e}")
            
    # Guardar en JSON invertido para que se vean los más recientes de primeros, o al menos ordenado original
    historial_final.reverse()
    
    with open('historial_auditoria.json', 'w', encoding='utf-8') as f:
        json.dump(historial_final, f, ensure_ascii=False, indent=4)
        
    logging.info(f"✅ ¡Auditoría construida! {len(historial_final)} partidos analizados.")

if __name__ == "__main__":
    generar_auditoria()
