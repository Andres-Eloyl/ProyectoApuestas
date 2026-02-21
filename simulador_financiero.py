import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def simular_apuestas():
    print("Iniciando el Backtesting Financiero...\n")
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
    predicciones = modelo.predict(X_test)

    capital_inicial = 1000.0
    capital_actual = capital_inicial
    apuesta_por_partido = 10.0 
    
    partidos_apostados = len(predicciones)
    apuestas_ganadas = 0

    print(f"💰 Capital Inicial de la simulación: ${capital_inicial}")
    print(f"📊 Apostando ${apuesta_por_partido} de forma plana a cada uno de los {partidos_apostados} partidos...\n")

    for i in range(partidos_apostados):
        prediccion = predicciones[i]
        resultado_real = y_test.iloc[i]
        
        cuota_H = cuotas_test.iloc[i]['B365H']
        cuota_D = cuotas_test.iloc[i]['B365D']
        cuota_A = cuotas_test.iloc[i]['B365A']

        capital_actual -= apuesta_por_partido

        if prediccion == resultado_real:
            apuestas_ganadas += 1
            if prediccion == 'H':
                ganancia = apuesta_por_partido * cuota_H
            elif prediccion == 'D':
                ganancia = apuesta_por_partido * cuota_D
            else: 
                ganancia = apuesta_por_partido * cuota_A
            
            capital_actual += ganancia

    beneficio_neto = capital_actual - capital_inicial
    roi = (beneficio_neto / capital_inicial) * 100
    
    print("=== REPORTE FINANCIERO FINAL ===")
    print(f"Aciertos del algoritmo: {apuestas_ganadas} de {partidos_apostados} ({(apuestas_ganadas/partidos_apostados)*100:.2f}%)")
    print(f"Capital Final en la cuenta: ${capital_actual:.2f}")
    
    if beneficio_neto > 0:
        print(f"Beneficio Neto: +${beneficio_neto:.2f} 🤑")
        print(f"Retorno de Inversión (ROI): +{roi:.2f}%")
        print("\n¡EL MODELO ES RENTABLE! Has vencido al mercado con estas 6 variables.")
    else:
        print(f"Pérdida Neta: ${beneficio_neto:.2f} 📉")
        print(f"Retorno de Inversión (ROI): {roi:.2f}%")
        print("\nEl modelo perdió dinero. El mercado de apuestas está cobrando su margen de comisión.")
        print("Solución para el ingeniero: Necesitamos incluir el 'xG' (Goles Esperados) o usar XGBoost.")

if __name__ == "__main__":
    simular_apuestas()