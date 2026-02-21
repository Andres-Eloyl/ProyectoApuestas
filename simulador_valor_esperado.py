import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def simular_valor_esperado():
    print("Iniciando el Backtesting de Valor Esperado (EV+)...\n")
    try:
        df = pd.read_csv('dataset_final_ml.csv')
    except FileNotFoundError:
        print("Error: No se encontró 'dataset_final_ml.csv'.")
        return

    features = ['Racha_Local', 'Racha_Visita', 'Dif_Goles_Local', 'Dif_Goles_Visita', 'Pts_Totales_Local', 'Pts_Totales_Visita']
    X = df[features]
    y = df['FTR']

    punto_corte = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:punto_corte], X.iloc[punto_corte:]
    y_train, y_test = y.iloc[:punto_corte], y.iloc[punto_corte:]
    
    cuotas_test = df[['B365H', 'B365D', 'B365A']].iloc[punto_corte:]

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    probabilidades = modelo.predict_proba(X_test)
    
    clases = list(modelo.classes_)
    idx_H = clases.index('H')
    idx_D = clases.index('D')
    idx_A = clases.index('A')

    capital_inicial = 1000.0
    capital_actual = capital_inicial
    apuesta_por_partido = 10.0 
    
    partidos_totales = len(X_test)
    apuestas_realizadas = 0
    apuestas_ganadas = 0
    
    margen_ventaja = 1.05 

    print(f"💰 Capital Inicial: ${capital_inicial}")
    print(f"Buscando errores en las cuotas de Bet365 en {partidos_totales} partidos...\n")

    for i in range(partidos_totales):
        resultado_real = y_test.iloc[i]
        
        prob_H = probabilidades[i][idx_H]
        prob_D = probabilidades[i][idx_D]
        prob_A = probabilidades[i][idx_A]
        
        cuota_H = cuotas_test.iloc[i]['B365H']
        cuota_D = cuotas_test.iloc[i]['B365D']
        cuota_A = cuotas_test.iloc[i]['B365A']

        ev_H = prob_H * cuota_H
        ev_D = prob_D * cuota_D
        ev_A = prob_A * cuota_A

        if ev_H > margen_ventaja:
            apuestas_realizadas += 1
            capital_actual -= apuesta_por_partido
            if resultado_real == 'H':
                apuestas_ganadas += 1
                capital_actual += (apuesta_por_partido * cuota_H)
                
        elif ev_D > margen_ventaja:
            apuestas_realizadas += 1
            capital_actual -= apuesta_por_partido
            if resultado_real == 'D':
                apuestas_ganadas += 1
                capital_actual += (apuesta_por_partido * cuota_D)
                
        elif ev_A > margen_ventaja:
            apuestas_realizadas += 1
            capital_actual -= apuesta_por_partido
            if resultado_real == 'A':
                apuestas_ganadas += 1
                capital_actual += (apuesta_por_partido * cuota_A)

    beneficio_neto = capital_actual - capital_inicial
    
    dinero_invertido = apuestas_realizadas * apuesta_por_partido
    roi = (beneficio_neto / dinero_invertido) * 100 if dinero_invertido > 0 else 0
    
    print("=== REPORTE FINANCIERO (VALUE BETTING) ===")
    print(f"Partidos analizados: {partidos_totales}")
    print(f"Apuestas realizadas (Filtro EV+): {apuestas_realizadas}")
    
    if apuestas_realizadas > 0:
        print(f"Aciertos del algoritmo: {apuestas_ganadas} de {apuestas_realizadas} ({(apuestas_ganadas/apuestas_realizadas)*100:.2f}%)")
        print(f"Capital Final: ${capital_actual:.2f}")
        
        if beneficio_neto > 0:
            print(f"Beneficio Neto: +${beneficio_neto:.2f} 🤑")
            print(f"Retorno de Inversión (Yield/ROI): +{roi:.2f}%")
            print("\n¡ALGORITMO RENTABLE! Lograste vencer la matemática de la casa de apuestas.")
        else:
            print(f"Pérdida Neta: ${beneficio_neto:.2f} 📉")
            print(f"Retorno de Inversión (Yield/ROI): {roi:.2f}%")
            print("\nEl modelo redujo pérdidas, pero aún necesita variables más predictivas (como xG).")
    else:
        print("\nEl modelo fue demasiado estricto y no encontró ninguna apuesta de valor.")

if __name__ == "__main__":
    simular_valor_esperado()
    