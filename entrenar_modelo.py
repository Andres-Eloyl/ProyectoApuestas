import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def entrenar_y_evaluar():
    print("Cargando el dataset inteligente...")
    try:
        df = pd.read_csv('dataset_final_ml.csv')
    except FileNotFoundError:
        print("Error: No se encontró 'dataset_final_ml.csv'.")
        return

    X = df[['Racha_Local', 'Racha_Visita', 'Dif_Goles_Local', 'Dif_Goles_Visita', 'Pts_Totales_Local', 'Pts_Totales_Visita']]
    y = df['FTR'] 

    punto_corte = int(len(df) * 0.8)
    
    X_train = X.iloc[:punto_corte]
    y_train = y.iloc[:punto_corte]
    
    X_test = X.iloc[punto_corte:]
    y_test = y.iloc[punto_corte:]

    print(f"Partidos para entrenar: {len(X_train)}")
    print(f"Partidos para examinar (Futuro simulado): {len(X_test)}\n")

    
    print("Entrenando el Bosque Aleatorio (Random Forest)...")
    
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    
   
    modelo.fit(X_train, y_train)

    print("Evaluando predicciones en los partidos de prueba...\n")
    predicciones = modelo.predict(X_test)
    
    precision = accuracy_score(y_test, predicciones)
    
    print("=== RESULTADOS DEL MODELO ===")
    print(f"Precisión Global (Accuracy): {precision * 100:.2f}%\n")
    
    
    print("=== REPORTE DETALLADO POR TIPO DE RESULTADO ===")
    print(classification_report(y_test, predicciones, zero_division=0))

entrenar_y_evaluar()