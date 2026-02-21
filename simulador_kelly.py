import pandas as pd
import logging
from modelos_poo import PredictorRandomForest

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class SimuladorFinancieroKelly:
    """Clase que maneja la lógica de inversión usando el Criterio de Kelly."""
    
    def __init__(self, modelo_predictivo, capital_inicial=1000.0, multiplicador_kelly=0.10):
        self.bot = modelo_predictivo
        self.capital = capital_inicial
        self.capital_inicial = capital_inicial
        self.multiplicador_kelly = multiplicador_kelly
        self.historial_apuestas = []

    def calcular_apuesta_kelly(self, probabilidad, cuota):
        """Aplica la fórmula matemática del Criterio de Kelly."""
        b = cuota - 1.0 
        q = 1.0 - probabilidad
        
        fraccion_kelly = probabilidad - (q / b)
        
        if fraccion_kelly <= 0:
            return 0.0
            
        fraccion_segura = fraccion_kelly * self.multiplicador_kelly
        
        fraccion_segura = min(fraccion_segura, 0.05)
        
        return self.capital * fraccion_segura

    def ejecutar_backtesting(self, X_test, y_test, cuotas_test):
        logging.info("Iniciando Backtesting con Gestión de Capital Dinámica (Kelly)...")
        
        probabilidades = self.bot.predecir_probabilidades(X_test)
        clases = list(self.bot.obtener_clases())
        idx_H, idx_D, idx_A = clases.index('H'), clases.index('D'), clases.index('A')

        for i in range(len(X_test)):
            resultado_real = y_test.iloc[i]
            
            prob_H = probabilidades[i][idx_H]
            prob_D = probabilidades[i][idx_D]
            prob_A = probabilidades[i][idx_A]
            
            cuota_H = cuotas_test.iloc[i]['B365H']
            cuota_D = cuotas_test.iloc[i]['B365D']
            cuota_A = cuotas_test.iloc[i]['B365A']

            apuesta_H = self.calcular_apuesta_kelly(prob_H, cuota_H)
            apuesta_D = self.calcular_apuesta_kelly(prob_D, cuota_D)
            apuesta_A = self.calcular_apuesta_kelly(prob_A, cuota_A)

            apuestas_posibles = {'H': apuesta_H, 'D': apuesta_D, 'A': apuesta_A}
            mejor_opcion = max(apuestas_posibles, key=apuestas_posibles.get)
            monto_a_apostar = apuestas_posibles[mejor_opcion]

            if monto_a_apostar > 1.0:
                self.capital -= monto_a_apostar
                cuota_acertada = {'H': cuota_H, 'D': cuota_D, 'A': cuota_A}[mejor_opcion]
                
                if mejor_opcion == resultado_real:
                    ganancia = monto_a_apostar * cuota_acertada
                    self.capital += ganancia
                    estado = "GANADA"
                else:
                    estado = "PERDIDA"
                    
                self.historial_apuestas.append({
                    'Prediccion': mejor_opcion, 'Real': resultado_real,
                    'Probabilidad': {'H': prob_H, 'D': prob_D, 'A': prob_A}[mejor_opcion],
                    'Cuota': cuota_acertada, 'Monto': monto_a_apostar, 'Estado': estado
                })

        self.generar_reporte()

    def generar_reporte(self):
        apuestas_totales = len(self.historial_apuestas)
        ganadas = sum(1 for a in self.historial_apuestas if a['Estado'] == 'GANADA')
        beneficio = self.capital - self.capital_inicial
        
        print("\n" + "="*40)
        print("📊 REPORTE FINANCIERO: CRITERIO DE KELLY")
        print("="*40)
        print(f"Apuestas realizadas: {apuestas_totales}")
        
        if apuestas_totales > 0:
            print(f"Tasa de Acierto: {(ganadas/apuestas_totales)*100:.2f}%")
            print(f"Capital Final: ${self.capital:.2f}")
            print(f"Beneficio Neto: ${beneficio:.2f}")
            roi = (beneficio / self.capital_inicial) * 100
            print(f"Retorno de Inversión (ROI total): {roi:.2f}%")
        else:
            print("El algoritmo fue ultra conservador y no encontró valor en ningún partido.")

if __name__ == "__main__":
    cerebro = PredictorRandomForest(ruta_csv='dataset_final_ml.csv')
    cerebro.cargar_datos()
    X_train, X_test, y_train, y_test = cerebro.preparar_datos_entrenamiento()
    
    if X_train is not None:
        cerebro.entrenar(X_train, y_train)
        
        cuotas_test = cerebro.df[['B365H', 'B365D', 'B365A']].iloc[int(len(cerebro.df) * 0.8):]
        
        banco = SimuladorFinancieroKelly(modelo_predictivo=cerebro, capital_inicial=1000.0)
        banco.ejecutar_backtesting(X_test, y_test, cuotas_test)
        