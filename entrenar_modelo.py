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

    # 1. Definir qué mira el modelo (X) y qué debe adivinar (y)
    # Solo le daremos nuestras variables creadas. 
    # (En un proyecto más grande, aquí agregarías xG, fatiga, lesiones, etc.)
    X = df[['Racha_Local', 'Racha_Visita', 'Dif_Goles_Local', 'Dif_Goles_Visita', 'Pts_Totales_Local', 'Pts_Totales_Visita']]
    y = df['FTR'] # FTR = Full Time Result (H=Local, D=Empate, A=Visita)

    # 2. División Cronológica (Time-Series Split)
    # No usamos la división aleatoria clásica. Tomamos el primer 80% de la temporada 
    # para estudiar y el último 20% para examinar.
    punto_corte = int(len(df) * 0.8)
    
    X_train = X.iloc[:punto_corte]
    y_train = y.iloc[:punto_corte]
    
    X_test = X.iloc[punto_corte:]
    y_test = y.iloc[punto_corte:]

    print(f"Partidos para entrenar: {len(X_train)}")
    print(f"Partidos para examinar (Futuro simulado): {len(X_test)}\n")

    # 3. Inicializar y Entrenar el Modelo
    print("Entrenando el Bosque Aleatorio (Random Forest)...")
    # n_estimators=100 significa que creará 100 árboles de decisión diferentes
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Aquí es donde ocurre el cálculo algebraico pesado
    modelo.fit(X_train, y_train)

    # 4. Evaluación del Modelo
    print("Evaluando predicciones en los partidos de prueba...\n")
    predicciones = modelo.predict(X_test)
    
    # Comparamos lo que predijo el modelo vs lo que realmente pasó
    precision = accuracy_score(y_test, predicciones)
    
    print("=== RESULTADOS DEL MODELO ===")
    print(f"Precisión Global (Accuracy): {precision * 100:.2f}%\n")
    
    
    print("=== REPORTE DETALLADO POR TIPO DE RESULTADO ===")
    # Este reporte nos dice en qué se equivoca más (ej. ¿Falla mucho prediciendo empates?)
    print(classification_report(y_test, predicciones, zero_division=0))

# Ejecutar la función principal
entrenar_y_evaluar()