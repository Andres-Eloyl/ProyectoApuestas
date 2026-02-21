import pandas as pd
import logging
from modelos_poo import PredictorRandomForest
from notificador import BotPredictscore

def sistema_alertas_produccion():
    logging.info("Iniciando Sistema de Alertas para el fin de semana del 20/02/2026...")
    bot_telegram = BotPredictscore()
    
    bot = PredictorRandomForest(ruta_csv='dataset_final_ml.csv')
    bot.cargar_datos()
    X, _, y, _ = bot.preparar_datos_entrenamiento(proporcion_train=1.0) 
    bot.entrenar(X, y)

    try:
        hoy = pd.read_csv('partidos_hoy.csv')
        

        X_hoy = hoy[bot.features] 
        
        probs = bot.predecir_probabilidades(X_hoy)
        clases = list(bot.obtener_clases())
    except Exception as e:
        print(f"Error al leer o predecir: {e}")
        return

    print("\n" + "═"*60)
    print("REPORTES DE INVERSIÓN")
    print("═"*60)

    for i in range(len(hoy)):
        p_h = probs[i][clases.index('H')]
        cuota_h = hoy.iloc[i]['B365H']
        ev = p_h * cuota_h
        equipo_l = hoy.iloc[i]['HomeTeam']
        equipo_v = hoy.iloc[i]['AwayTeam']

        prob_local = p_h * 100 

        if prob_local >= 60:
            nivel_confianza = "🟢 ALTA"
            texto_apuesta = f"Te recomendamos apostar a la **Victoria de {equipo_l} (1X2)**. La IA tiene gran seguridad en este resultado."
        elif prob_local >= 45:
            nivel_confianza = "🟡 MEDIA"
            texto_apuesta = f"Te recomendamos apostar a la **Victoria de {equipo_l} (1X2)**. Es un pick de valor, pero modera el monto de inversión."
        else:
            nivel_confianza = "🔴 RIESGO (BUSCANDO LA SORPRESA)"
            texto_apuesta = f"Te recomendamos apostar a la **Victoria de {equipo_l} (1X2)** porque las casas de apuestas subestimaron sus probabilidades reales. Apuesta de alto riesgo."

        mensaje = f"""🔥 ALERTA DE INVERSIÓN: PREDICTSCORE 🔥

⚽ {equipo_l} vs {equipo_v}
📊 Probabilidad IA (Local): {prob_local:.1f}%
🏦 Cuota Encontrada: {cuota_h}
📈 Valor Esperado (EV): {ev:.2f}
⚡ Confianza de la IA: {nivel_confianza}

💡 Recomendación del día: {texto_apuesta}"""

        if ev > 1.0:
            print(f"🔥 [ALERTA DE VALOR] Enviando {equipo_l} a Telegram...")
            
            bot_telegram.enviar_mensaje(mensaje) 
        else:
            print(f"❌ [SIN VALOR] {equipo_l} descartado (EV: {ev:.2f})")

if __name__ == "__main__":
    sistema_alertas_produccion()