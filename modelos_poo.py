import pandas as pd
import logging
import numpy as np
from scipy.stats import poisson
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.calibration import CalibratedClassifierCV

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class PredictorDeportivoBase:
    """Clase base que define el esqueleto de cualquier modelo predictivo."""
    
    def __init__(self, ruta_csv: str):
        self.ruta_csv = ruta_csv
        self.df = None
        self.modelo_calibrado = None
        self.features = ['Racha_Local', 'Racha_Visita', 'Dif_Goles_Local', 
                         'Dif_Goles_Visita', 'Pts_Totales_Local', 'Pts_Totales_Visita']

    def cargar_datos(self):
        """Carga el dataset desde el archivo CSV."""
        try:
            self.df = pd.read_csv(self.ruta_csv)
            logging.info(f"Datos cargados exitosamente: {len(self.df)} partidos.")
        except FileNotFoundError:
            logging.error(f"No se encontró el archivo: {self.ruta_csv}")
            
    def preparar_datos_entrenamiento(self, proporcion_train=0.8):
        """Divide los datos cronológicamente (80% entrenamiento, 20% prueba)."""
        if self.df is None:
            logging.error("No hay datos cargados.")
            return None, None, None, None
            
        X = self.df[self.features]
        y = self.df['FTR']
        
        corte = int(len(self.df) * proporcion_train)
        logging.info(f"Datos divididos en punto de corte: {corte}")
        return X.iloc[:corte], X.iloc[corte:], y.iloc[:corte], y.iloc[corte:]

class PredictorRandomForest(PredictorDeportivoBase):
    """Modelo especializado en Random Forest con optimización de parámetros."""
    
    def entrenar(self, X_train, y_train):
        logging.info("Iniciando búsqueda de hiperparámetros óptimos (GridSearch)...")
        
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [None, 5, 10],
            'min_samples_split': [2, 5]
        }
        
        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=42), 
            param_grid, 
            cv=3, 
            scoring='accuracy'
        )
        grid_search.fit(X_train, y_train)
        
        logging.info(f"Mejores parámetros encontrados: {grid_search.best_params_}")

        logging.info("Calibrando probabilidades (Escalamiento de Platt)...")
        self.modelo_calibrado = CalibratedClassifierCV(
            grid_search.best_estimator_, 
            method='sigmoid', 
            cv=5
        )
        self.modelo_calibrado.fit(X_train, y_train)
        logging.info("¡Entrenamiento y Calibración finalizados con éxito!")

    def predecir_probabilidades(self, X_test):
        """Devuelve las probabilidades calibradas para cada resultado."""
        if self.modelo_calibrado is None:
            logging.error("El modelo no ha sido entrenado.")
            return None
        return self.modelo_calibrado.predict_proba(X_test)

    def obtener_clases(self):
        """Retorna el orden de las etiquetas (ej. ['A', 'D', 'H'])."""
        return self.modelo_calibrado.classes_

class PredictorGradientBoosting(PredictorDeportivoBase):
    """Modelo avanzado usando Gradient Boosting para mayor precisión ante relaciones no lineales."""
    
    def entrenar(self, X_train, y_train):
        logging.info("Entrenando motor avanzado (HistGradientBoosting)...")
        
        modelo_base = HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.05,
            max_depth=7,
            min_samples_leaf=10,
            random_state=42
        )
        
        logging.info("Calibrando probabilidades...")
        self.modelo_calibrado = CalibratedClassifierCV(
            modelo_base,
            method='sigmoid',
            cv=5
        )
        self.modelo_calibrado.fit(X_train, y_train)
        logging.info("¡Motor HistGradient calibrado con éxito!")

    def predecir_probabilidades(self, X_test):
        if self.modelo_calibrado is None:
            logging.error("El modelo no ha sido entrenado.")
            return None
        return self.modelo_calibrado.predict_proba(X_test)

    def obtener_clases(self):
        return self.modelo_calibrado.classes_

class PredictorGolesPoisson:
    """Calcula resultados exactos basados en la distribución matemática de Poisson y Expectativa de Goles."""
    
    @staticmethod
    def predecir_marcador(xg_local: float, xg_visita: float, max_goles=5):
        """Genera una matriz bivariada de poisson y retorna el marcador más probable y expectativas."""
        # Se añade un leve factor multiplicativo/ajuste casa-fuera implícito si el xG lo requiere 
        # (Acá asumimos que el xG ya viene ponderado, pero podemos darle al local un x1.1 clásico de fútbol)
        lambda_local = max(0.1, xg_local * 1.05)
        lambda_visita = max(0.1, xg_visita * 0.95)
        
        max_prob = 0.0
        mejor_marcador = "0-0"
        
        # GridSearch 5x5 para encontrar el marcador exacto más probable
        for goles_l in range(max_goles + 1):
            for goles_v in range(max_goles + 1):
                # Asumimos independencia (Poisson simple)
                prob = poisson.pmf(goles_l, lambda_local) * poisson.pmf(goles_v, lambda_visita)
                if prob > max_prob:
                    max_prob = prob
                    mejor_marcador = f"{goles_l}-{goles_v}"
                    
        return round(lambda_local, 2), round(lambda_visita, 2), mejor_marcador

if __name__ == "__main__":
    bot = PredictorGradientBoosting(ruta_csv='dataset_final_ml.csv')
    bot.cargar_datos()
    X_tr, X_te, y_tr, y_te = bot.preparar_datos_entrenamiento()
    
    if X_tr is not None:
        bot.entrenar(X_tr, y_tr)
        print("\n✅ El nuevo modelo de Gradient Boosting está listo y calibrado.")