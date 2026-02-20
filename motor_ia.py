import pandas as pd
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.calibration import CalibratedClassifierCV

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class PredictorDeportivo:
    def __init__(self):
        self.features = ['Racha_Local', 'Racha_Visita', 'Dif_Goles_Local', 
                         'Dif_Goles_Visita', 'Pts_Totales_Local', 'Pts_Totales_Visita']
        self.modelo_calibrado = None
        self.clases = None

    def entrenar(self, df_historico):
        logging.info("Optimizando Cerebro (GridSearch + Calibración)...")
        X = df_historico[self.features]
        y = df_historico['FTR']
        
        # 1. Buscamos la mejor configuración
        param_grid = {'n_estimators': [100, 200], 'max_depth': [5, 10, None]}
        gs = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3)
        gs.fit(X, y)
        
        # 2. Calibramos para tener probabilidades reales (Platt Scaling)
        self.modelo_calibrado = CalibratedClassifierCV(gs.best_estimator_, method='sigmoid', cv=5)
        self.modelo_calibrado.fit(X, y)
        self.clases = list(self.modelo_calibrado.classes_)
        logging.info("✅ Modelo listo para producción.")

    def predecir(self, df_nuevos):
        probs = self.modelo_calibrado.predict_proba(df_nuevos[self.features])
        return probs, self.clases

class GestorFinanciero:
    @staticmethod
    def calcular_kelly(prob, cuota, multiplicador=0.1):
        """Calcula la fracción del capital a invertir (Fractional Kelly)."""
        b = cuota - 1
        q = 1 - prob
        f_star = prob - (q / b)
        return max(0, f_star * multiplicador) # Nunca apostar si el valor es negativo