⚽ AI Sports Betting Engine - Predictor 2026
📌 Descripción del Proyecto
Este sistema es un motor de análisis predictivo. El objetivo central es identificar valor matemático en los mercados de apuestas deportivas mediante modelos de Machine Learning calibrados y gestión de riesgo financiero.

A diferencia de modelos convencionales, este motor utiliza Calibración de Platt para asegurar que las probabilidades emitidas por la IA coincidan con la frecuencia real de los eventos históricos, evitando sesgos de sobreconfianza.

🛠️ Tecnologías Utilizadas
Lenguaje: Python 3.10+.

Machine Learning: Scikit-learn (Random Forest), XGBoost.

Procesamiento de Datos: Pandas y Numpy para ingeniería de variables.

Optimización: GridSearchCV para el ajuste fino de hiperparámetros.

🏗️ Arquitectura del Software
El proyecto sigue principios de Programación Orientada a Objetos (POO) para garantizar la escalabilidad y el mantenimiento del código:

Ingesta de Datos (ingesta_datos.py): Automatiza la descarga y limpieza de datos históricos de las temporadas 24/25 y 25/26.

Feature Engineering (ingenieria_caracteristicas.py): Transforma los resultados brutos en métricas de rendimiento como Rachas, Diferencia de Goles y Puntos Totales.

Motor de IA (motor_ia.py): Implementa modelos calibrados para generar probabilidades honestas.

Simuladores Financieros: Módulos que aplican el Criterio de Kelly y el Valor Esperado (EV) para decidir si una apuesta es viable o no.

📊 Caso de Estudio: Jornada Feb 2026
El sistema fue validado con partidos de la jornada del 20 de febrero de 2026, demostrando una capacidad crítica de filtrado al detectar cuotas con Valor Esperado negativo y recomendando la protección del capital frente a cuotas ineficientes en partidos de alta volatilidad.

🚀 Próximos Pasos (Roadmap)
Integración de una API de cuotas en tiempo real.

Implementación de modelos basados en Goles Esperados (xG).

Desarrollo de un bot de Telegram para alertas de valor automáticas.

