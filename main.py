import pandas as pd
import logging
from motor_ia import PredictorDeportivo, GestorFinanciero

def procesar_caracteristicas(df):
    """Ingeniería de variables en tiempo real."""
    stats = {}
    r_l, r_v, dg_l, dg_v, pts_l, pts_v = [], [], [], [], [], []
    
    for _, fila in df.iterrows():
        l, v, res = fila['HomeTeam'], fila['AwayTeam'], fila['FTR']
        gl, gv = fila['FTHG'], fila['FTAG']
        
        for e in [l, v]:
            if e not in stats: stats[e] = {'p':[], 'gf':[], 'gc':[], 'total':0}
        
        r_l.append(sum(stats[l]['p'][-3:])); r_v.append(sum(stats[v]['p'][-3:]))
        dg_l.append(sum(stats[l]['gf'][-3:]) - sum(stats[l]['gc'][-3:]))
        dg_v.append(sum(stats[v]['gf'][-3:]) - sum(stats[v]['gc'][-3:]))
        pts_l.append(stats[l]['total']); pts_v.append(stats[v]['total'])
        
        stats[l]['gf'].append(gl); stats[l]['gc'].append(gv)
        stats[v]['gf'].append(gv); stats[v]['gc'].append(gl)
        if res == 'H': stats[l]['total']+=3
        elif res == 'A': stats[v]['total']+=3
        else: stats[l]['total']+=1; stats[v]['total']+=1
            
    df['Racha_Local'], df['Racha_Visita'] = r_l, r_v
    df['Dif_Goles_Local'], df['Dif_Goles_Visita'] = dg_l, dg_v
    df['Pts_Totales_Local'], df['Pts_Totales_Visita'] = pts_l, pts_v
    return df

def ejecutar_sistema():
    url = "https://www.football-data.co.uk/mmz4281/2526/SP1.csv"
    logging.info(f"Descargando temporada actual: 20/02/2026")
    df_raw = pd.read_csv(url)
    df_hist = procesar_caracteristicas(df_raw)

    ia = PredictorDeportivo()
    ia.entrenar(df_hist)
    
    try:
        df_hoy = pd.read_csv('partidos_hoy.csv')
        probs, clases = ia.predecir(df_hoy)
        
        print("\n" + "="*50)
        print(f"🚀 ALERTAS DE VALOR - {pd.Timestamp.now().strftime('%d/%m/%Y')}")
        print("="*50)
        
        for i, fila in df_hoy.iterrows():

            p_h = probs[i][clases.index('H')]
            cuota_h = fila['B365H']
            ev = p_h * cuota_h
            kelly = GestorFinanciero.calcular_kelly(p_h, cuota_h)
            
            print(f"\n🏟️  {fila['HomeTeam']} vs {fila['AwayTeam']}")
            print(f"   Probabilidad Local: {p_h:.1%} | Cuota: {cuota_h} | EV: {ev:.2f}")
            
            if ev > 1.10: 
                print(f"   💰 RECOMENDACIÓN: Invertir {kelly:.1%} del capital.")
            else:
                print(f"   ❌ Sin valor suficiente.")
                
    except FileNotFoundError:
        logging.error("No se encontró 'partidos_hoy.csv'.")

if __name__ == "__main__":
    ejecutar_sistema()
    