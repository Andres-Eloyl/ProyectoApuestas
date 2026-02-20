import pandas as pd
import logging
from modelos_poo import PredictorRandomForest

def sistema_alertas_produccion():
    logging.info("Iniciando Sistema de Alertas para el fin de semana del 20/02/2026...")
    
    # 1. Cargamos y entrenamos el cerebro con el dataset total
    bot = PredictorRandomForest(ruta_csv='dataset_final_ml.csv')
    bot.cargar_datos()
    X, _, y, _ = bot.preparar_datos_entrenamiento(proporcion_train=1.0) # Entrenamos con TODO
    bot.entrenar(X, y)

    # 2. Leemos la cartelera de hoy
    # ... (dentro de la función sistema_alertas_produccion)

    # 2. Leemos la cartelera de hoy
    try:
        hoy = pd.read_csv('partidos_hoy.csv')
        
        # EL AJUSTE ESTÁ AQUÍ: 
        # Filtramos 'hoy' para que solo pasen las variables numéricas (features)
        X_hoy = hoy[bot.features] 
        
        # Ahora sí, le pasamos solo lo que el modelo reconoce
        probs = bot.predecir_probabilidades(X_hoy)
        clases = list(bot.obtener_clases())
    except Exception as e:
        print(f"Error al leer o predecir: {e}")
        return

# ... (el resto del bucle for queda igual)

    print("\n" + "═"*60)
    print("REPORTES DE INVERSIÓN")
    print("═"*60)

    for i in range(len(hoy)):
        # Extraemos probabilidad de victoria Local (H)
        p_h = probs[i][clases.index('H')]
        cuota_h = hoy.iloc[i]['B365H']
        
        # Fórmula de Valor Esperado
        ev = p_h * cuota_h
        
        equipo_l = hoy.iloc[i]['HomeTeam']
        equipo_v = hoy.iloc[i]['AwayTeam']

        print(f"\n⚽ {equipo_l} vs {equipo_v}")
        print(f"   🔹 Probabilidad Local: {p_h:.1%}")
        print(f"   🔹 Cuota Bet365: {cuota_h}")
        print(f"   🔹 Valor Esperado (EV): {ev:.2f}")

        # Umbral de decisión
        if ev > 1.15:
            print(f"   🔥 [ALERTA DE VALOR] La cuota está inflada. Posible ganancia a largo plazo.")
        elif ev > 1.05:
            print(f"   ✅ [VALOR MODERADO] Inversión razonable.")
        else:
            print(f"   ❌ [SIN VALOR] La casa de apuestas tiene la ventaja.")

if __name__ == "__main__":
    sistema_alertas_produccion()
