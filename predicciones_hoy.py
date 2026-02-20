import pandas as pd
import logging
from modelos_poo import PredictorRandomForest

def predecir_jornada_actual():
    # 1. Cargamos el cerebro optimizado
    bot = PredictorRandomForest(ruta_csv='dataset_final_ml.csv')
    bot.cargar_datos()
    
    # Entrenamos con todos los datos históricos disponibles para máxima potencia
    X = bot.df[bot.features]
    y = bot.df['FTR']
    bot.entrenar(X, y)

    # 2. Cargar los partidos que se juegan hoy
    try:
        hoy_df = pd.read_csv('partidos_hoy.csv')
    except FileNotFoundError:
        print("\n⚠️ Error: Crea el archivo 'partidos_hoy.csv' con los datos de hoy.")
        return

    # Extraemos las características para que el bot las analice
    X_hoy = hoy_df[bot.features]
    probs = bot.predecir_probabilidades(X_hoy)
    clases = list(bot.obtener_clases())
    
    print("\n" + "="*50)
    print("🎯 PREDICCIONES DEL MODELO CALIBRADO (PRODUCCIÓN)")
    print("="*50)

    for i in range(len(hoy_df)):
        p_h = probs[i][clases.index('H')]
        p_d = probs[i][clases.index('D')]
        p_a = probs[i][clases.index('A')]
        
        home = hoy_df.iloc[i]['HomeTeam']
        away = hoy_df.iloc[i]['AwayTeam']
        c_h = hoy_df.iloc[i]['B365H']
        
        # Calculamos el Valor Esperado (EV) para el local
        ev_h = p_h * c_h
        
        print(f"\n🏟️  {home} vs {away}")
        print(f"   Probabilidades -> Local: {p_h:.1%} | Empate: {p_d:.1%} | Visita: {p_a:.1%}")
        print(f"   Cuota Local: {c_h} | Valor Esperado (EV): {ev_h:.2f}")
        
        # Umbral estricto: Solo recomienda si el EV es mayor a 1.10 (10% de ventaja)
        if ev_h > 1.10:
            print(f"   ✅ RECOMENDACIÓN: Apostar a {home} (Ventaja matemática encontrada)")
        else:
            print(f"   ❌ NO APOSTAR: No hay valor suficiente en la cuota.")

if __name__ == "__main__":
    predecir_jornada_actual()