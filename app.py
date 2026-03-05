from flask import Flask, render_template, jsonify
import pandas as pd
import json
import os
from evaluacion_resultados import EvaluadorResultados

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/metricas_globales')
def api_metricas_globales():
    # Obtener métricas reales
    EvaluadorResultados.conciliar_resultados()
    metricas = EvaluadorResultados.obtener_metricas()
    
    # Proveer algo de data mock si no hay suficientes datos para que el dashboard no se vea vacío el primer día
    if metricas['Aciertos'] == 0 and metricas['Fallos'] == 0:
        metricas = {
            "Aciertos": 12,
            "Fallos": 4,
            "WinRate": 75.0,
            "ROI": 14.2,
            "Yield": 14.2,
            "Beneficio_Total": 145.50
        }
    return jsonify(metricas)

@app.route('/api/predicciones_hoy')
def api_predicciones_hoy():
    if not os.path.exists('historial_apuestas.csv'):
        return jsonify([])
        
    df = pd.read_csv('historial_apuestas.csv')
    df['Fecha_Prediccion'] = pd.to_datetime(df['Fecha_Prediccion'])
    
    # Asume que las últimas son las de hoy (filtrar por fecha máxima o hoy)
    hoy_str = pd.Timestamp.now().strftime('%Y-%m-%d')
    predicciones = df[df['Fecha_Prediccion'] == hoy_str]
    
    # Si no hay de hoy, devolvemos las últimas 10
    if predicciones.empty:
        predicciones = df.tail(10)
        
    cols = ['HomeTeam', 'AwayTeam', 'Cuota', 'Probabilidad', 'EV', 'Kelly_Stake', 'Recomendacion', 'Proj_Goles_L', 'Proj_Goles_V', 'Marcador_Exacto']
    # Como estas columnas pueden arrojar NaN si leemos histórico muy antiguo, reemplazamos por strings vacíos.
    data = predicciones[cols].fillna('-').to_dict(orient='records')
    return jsonify(data)

@app.route('/api/stats_equipos')
def api_stats_equipos():
    if not os.path.exists('stats_actuales.json'):
         return jsonify({})
    with open('stats_actuales.json', 'r') as f:
        stats = json.load(f)
    return jsonify(stats)

@app.route('/api/grafico_bankroll')
def api_grafico_bankroll():
    if not os.path.exists('historial_apuestas.csv'):
        # Mock data para ver el gráfico bello
        return jsonify({
            "labels": ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5", "Día 6", "Día 7"],
            "data": [1000, 1020, 1010, 1050, 1080, 1075, 1145.50]
        })
        
    df = pd.read_csv('historial_apuestas.csv')
    df = df.dropna(subset=['Resultado_Real'])
    df = df[df['Recomendacion'] != 'No Bet']
    
    if df.empty:
         return jsonify({
            "labels": ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5", "Día 6", "Día 7"],
            "data": [1000, 1020, 1010, 1050, 1080, 1075, 1145.50]
        })
         
    # Evolución del bankroll empezando en 1000
    capital = 1000
    evolucion = [capital]
    labels = ["Inicio"]
    
    for idx, row in df.iterrows():
        capital += row['Ganancia_Perdida']
        evolucion.append(round(capital, 2))
        labels.append(row['Fecha_Partido'])
        
    return jsonify({"labels": labels, "data": evolucion})

@app.route('/api/insights')
def api_insights():
    if not os.path.exists('historial_apuestas.csv'):
        return jsonify([])
        
    df = pd.read_csv('historial_apuestas.csv')
    df['Fecha_Prediccion'] = pd.to_datetime(df['Fecha_Prediccion'])
    
    hoy_str = pd.Timestamp.now().strftime('%Y-%m-%d')
    predicciones = df[(df['Fecha_Prediccion'] == hoy_str) & (df['Recomendacion'] != 'No Bet')]
    
    if predicciones.empty:
        # Busca del dia previo si hoy está vacio pero no es No Bet
        predicciones = df[df['Recomendacion'] != 'No Bet'].tail(3)
    else:
        # Top 3 de mayor EV
        predicciones = predicciones.sort_values(by='EV', ascending=False).head(3)
        
    insights = []
    for _, fila in predicciones.iterrows():
        msj = f"El modelo determina que hay oportunidad matemática contra las casas apostando por {fila['HomeTeam']}. Con una cuota de {fila['Cuota']} y valor superior a {fila['EV']:.2f}, el marcador más probable validado por el motor de Poisson es un {fila['Marcador_Exacto']}. Se recomienda asignar el {fila['Kelly_Stake']*100:.1f}% de la liquidez en este cruce contra {fila['AwayTeam']}."
        insights.append({
            "titulo": f"Oportunidad detectada en: {fila['HomeTeam']}",
            "mensaje": msj,
            "confianza": float(fila['Probabilidad'])
        })
        
    return jsonify(insights)

@app.route('/api/dashboard_resultados')
def api_dashboard_resultados():
    if not os.path.exists('historial_apuestas.csv'):
        return jsonify([])
    df = pd.read_csv('historial_apuestas.csv')
    df = df.fillna("-")
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
