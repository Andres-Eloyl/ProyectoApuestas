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

        print(f"\n⚽ {equipo_l} vs {equipo_v}")
        print(f"   🔹 Probabilidad Local: {p_h:.1%}")
        print(f"   🔹 Cuota Bet365: {cuota_h}")
        print(f"   🔹 Valor Esperado (EV): {ev:.2f}")

        if ev > 1.05:  
            print(f"   🔥 [ALERTA DE VALOR] Enviando a Telegram...")
            bot_telegram.enviar_alerta_valor(equipo_l, equipo_v, p_h, cuota_h, ev)
        elif ev > 1.05:
            print(f"   ✅ [VALOR MODERADO] Inversión razonable.")
        else:
            print(f"   ❌ [SIN VALOR] La casa de apuestas tiene la ventaja.")

if __name__ == "__main__":
    sistema_alertas_produccion()
