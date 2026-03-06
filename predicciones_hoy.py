import pandas as pd
import logging
import json
from modelos_poo import PredictorGradientBoosting, PredictorGolesPoisson
from evaluacion_resultados import EvaluadorResultados

def predecir_jornada_actual():
    # Cargar el modelo avanzado histórico
    bot = PredictorGradientBoosting(ruta_csv='dataset_final_ml.csv')
    bot.cargar_datos()
    
    # Aseguramos que utilice las features más potentes descubiertas
    bot.features = ['Racha_Local', 'Racha_Visita', 'Dif_Goles_Local', 
                    'Dif_Goles_Visita', 'Pts_Totales_Local', 'Pts_Totales_Visita',
                    'xG_Favor_Local', 'xG_Contra_Local', 'xG_Favor_Visita', 'xG_Contra_Visita']
    
    X = bot.df[bot.features]
    y = bot.df['FTR']
    bot.entrenar(X, y)

    try:
        hoy_df = pd.read_csv('partidos_hoy.csv')
    except FileNotFoundError:
        print("\n⚠️ Error: Crea el archivo 'partidos_hoy.csv' con los datos de hoy.")
        return

    try:
        with open('stats_actuales.json', 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        print("\n⚠️ Error: No se encontró 'stats_actuales.json'. Ejecuta la ingeniería primero.")
        return

    for idx, fila in hoy_df.iterrows():
        local, visita = fila['HomeTeam'], fila['AwayTeam']
        s_l = stats.get(local, {'Racha':0, 'Dif_Goles':0, 'xG_Favor':1.2, 'xG_Contra':1.2, 'Pts_Totales':0})
        s_v = stats.get(visita, {'Racha':0, 'Dif_Goles':0, 'xG_Favor':1.2, 'xG_Contra':1.2, 'Pts_Totales':0})
        
        hoy_df.at[idx, 'Racha_Local'] = s_l['Racha']
        hoy_df.at[idx, 'Dif_Goles_Local'] = s_l['Dif_Goles']
        hoy_df.at[idx, 'xG_Favor_Local'] = s_l['xG_Favor']
        hoy_df.at[idx, 'xG_Contra_Local'] = s_l['xG_Contra']
        hoy_df.at[idx, 'Pts_Totales_Local'] = s_l['Pts_Totales']
        
        hoy_df.at[idx, 'Racha_Visita'] = s_v['Racha']
        hoy_df.at[idx, 'Dif_Goles_Visita'] = s_v['Dif_Goles']
        hoy_df.at[idx, 'xG_Favor_Visita'] = s_v['xG_Favor']
        hoy_df.at[idx, 'xG_Contra_Visita'] = s_v['xG_Contra']
        hoy_df.at[idx, 'Pts_Totales_Visita'] = s_v['Pts_Totales']

    X_hoy = hoy_df[bot.features]
    probs = bot.predecir_probabilidades(X_hoy)
    clases = list(bot.obtener_clases())
    
    print("\n" + "="*50)
    print("PREDICCIONES DEL MOTOR XGB/BOOST (PRODUCCIÓN)")
    print("="*50)

    for i in range(len(hoy_df)):
        p_h = probs[i][clases.index('H')]
        p_d = probs[i][clases.index('D')]
        p_a = probs[i][clases.index('A')]
        
        home = hoy_df.iloc[i]['HomeTeam']
        away = hoy_df.iloc[i]['AwayTeam']
        c_h = hoy_df.iloc[i]['B365H']
        
        ev_h = p_h * c_h
        
        b = c_h - 1
        q = 1 - p_h
        kelly_frac = max(0, (p_h - (q / b)) * 0.1) if b > 0 else 0
        
        # --- NUEVO: Simulación de Marcador (Poisson) ---
        xg_l = hoy_df.iloc[i]['xG_Favor_Local']
        xg_v = hoy_df.iloc[i]['xG_Favor_Visita']
        g_l, g_v, marcador_exacto = PredictorGolesPoisson.predecir_marcador(xg_l, xg_v)
        
        print(f"\n  {home} vs {away}")
        print(f"   Probabilidades -> Local: {p_h:.1%} | Empate: {p_d:.1%} | Visita: {p_a:.1%}")
        print(f"   Cuota Local: {c_h} | Valor Esperado (EV): {ev_h:.2f}")
        print(f"   Simulación Goles -> Local: {g_l} | Visita: {g_v}")
        print(f"   Marcador Exacto Más Probable -> {marcador_exacto}")
        
        recomendacion = "No Bet"
        if ev_h > 1.10:
            print(f"   RECOMENDACIÓN: Apostar a {home} (Invertir {kelly_frac:.2%} del bank)")
            recomendacion = "H"
        else:
            print(f"   NO APOSTAR: No hay valor suficiente en la cuota.")
            
        from datetime import timedelta
        # Asignamos la fecha del partido a mañana
        fecha_partido = (pd.Timestamp.now() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        EvaluadorResultados.registrar_prediccion(
            fecha=fecha_partido, local=home, visita=away, cuota=c_h, 
            prob=p_h, ev=ev_h, kelly=kelly_frac, recomendacion=recomendacion,
            goles_l=g_l, goles_v=g_v, marcador=marcador_exacto
        )
        
    print("\n Estadísticas Generales Actualizadas:")
    EvaluadorResultados.conciliar_resultados()
    print(EvaluadorResultados.obtener_metricas())

if __name__ == "__main__":
    predecir_jornada_actual()