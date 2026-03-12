import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def entrenar_y_evaluar():
    """
    Entrena y evalúa un modelo base RandomForest para predecir resultados de partidos.
    Divide el dataset en 80% entrenamiento y 20% prueba, e imprime métricas de clasificación.
    """
    print("Cargando el dataset...")
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

    print(f"Instancias de entrenamiento: {len(X_train)}")
    print(f"Instancias de prueba: {len(X_test)}\n")

    print("Iniciando entrenamiento avanzado (HistGradientBoosting)...")
    
    # Instanciamos nuestra clase de BOOSTER
    from modelos_poo import PredictorGradientBoosting
    
    bot = PredictorGradientBoosting(ruta_csv="dataset_final_ml.csv")
    
    # Asignamos temporalmente el dataframe a procesar para el bot
    bot.df = df
    X_train_full = bot.df[bot.features]
    y_train_full = bot.df['FTR']
    
    bot.entrenar(X_train_full, y_train_full)
    
    # Guardamos el modelo
    bot.guardar_modelo("modelo_gbm.joblib")

    print("\nEvaluando predicciones en los partidos de prueba...\n")
    # Para evaluar reusamos el clasificador subyacente de la clase (calibrado)
    predicciones = bot.modelo_calibrado.predict(X_test)
    
    precision = accuracy_score(y_test, predicciones)
    
    print("=== RESULTADOS DEL MODELO ===")
    print(f"Precisión Global (Accuracy): {precision * 100:.2f}%\n")
    
    
    print("=== REPORTE DETALLADO POR TIPO DE RESULTADO ===")
    print(classification_report(y_test, predicciones, zero_division=0))

entrenar_y_evaluar()