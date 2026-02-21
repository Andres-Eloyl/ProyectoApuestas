import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

def simular_apuestas_xgboost():
    print("Iniciando el Backtesting Financiero con XGBoost...\n")
    try:
        df = pd.read_csv('dataset_final_ml.csv')
    except FileNotFoundError:
        print("Error: No se encontró 'dataset_final_ml.csv'.")
        return

    features = ['Racha_Local', 'Racha_Visita', 'Dif_Goles_Local', 'Dif_Goles_Visita', 'Pts_Totales_Local', 'Pts_Totales_Visita']
    X = df[features]
    y = df['FTR']

    codificador = LabelEncoder()
    y_numerico = codificador.fit_transform(y)

    punto_corte = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:punto_corte], X.iloc[punto_corte:]
    y_train, y_test = y_numerico[:punto_corte], y_numerico[punto_corte:]
    
    cuotas_test = df[['B365H', 'B365D', 'B365A']].iloc[punto_corte:]

    modelo_xgb = XGBClassifier(n_estimators=100, learning_rate=0.1, eval_metric='mlogloss', random_state=42)
    modelo_xgb.fit(X_train, y_train)
    
    predicciones_numericas = modelo_xgb.predict(X_test)
    predicciones = codificador.inverse_transform(predicciones_numericas)
    
    y_test_texto = codificador.inverse_transform(y_test)

    capital_inicial = 1000.0
    capital_actual = capital_inicial
    apuesta_por_partido = 10.0 
    
    partidos_apostados = len(predicciones)
    apuestas_ganadas = 0

    print(f"💰 Capital Inicial: ${capital_inicial}")
    print(f"📊 Apostando ${apuesta_por_partido} por partido...\n")

    for i in range(partidos_apostados):
        pred = predicciones[i]
        real = y_test_texto[i]
        
        cuota_H = cuotas_test.iloc[i]['B365H']
        cuota_D = cuotas_test.iloc[i]['B365D']
        cuota_A = cuotas_test.iloc[i]['B365A']

        capital_actual -= apuesta_por_partido

        if pred == real:
            apuestas_ganadas += 1
            if pred == 'H':
                ganancia = apuesta_por_partido * cuota_H
            elif pred == 'D':
                ganancia = apuesta_por_partido * cuota_D
            else:
                ganancia = apuesta_por_partido * cuota_A
            
            capital_actual += ganancia

    # 4. REPORTE EJECUTIVO
    beneficio_neto = capital_actual - capital_inicial
    roi = (beneficio_neto / capital_inicial) * 100
    
    print("=== REPORTE FINANCIERO FINAL (XGBOOST) ===")
    print(f"Aciertos del algoritmo: {apuestas_ganadas} de {partidos_apostados} ({(apuestas_ganadas/partidos_apostados)*100:.2f}%)")
    print(f"Capital Final: ${capital_actual:.2f}")
    
    if beneficio_neto > 0:
        print(f"Beneficio Neto: +${beneficio_neto:.2f} 🤑")
        print(f"Retorno de Inversión (ROI): +{roi:.2f}%")
        print("\n¡ALGORITMO RENTABLE! XGBoost encontró el margen de valor en el mercado.")
    else:
        print(f"Pérdida Neta: ${beneficio_neto:.2f} 📉")
        print(f"Retorno de Inversión (ROI): {roi:.2f}%")
        print("\nEl modelo sigue sin superar el margen de la casa de apuestas.")

if __name__ == "__main__":
    simular_apuestas_xgboost()