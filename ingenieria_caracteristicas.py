import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def generar_dataset_ml():
    logging.info("Iniciando ingeniería de características...")
    try:
        df = pd.read_csv('partidos_procesados.csv')
    except FileNotFoundError:
        logging.error("No se encontró 'partidos_procesados.csv'. Ejecuta la ingesta primero.")
        return

    stats = {}

    features_lista = []

    for i, fila in df.iterrows():
        local = fila['HomeTeam']
        visita = fila['AwayTeam']
        resultado = fila['FTR']
        goles_l = fila['FTHG']
        goles_v = fila['FTAG']

        for equipo in [local, visita]:
            if equipo not in stats:
                stats[equipo] = {'puntos_hist': [], 'goles_f': [], 'goles_c': [], 'total_pts': 0}

        racha_l = sum(stats[local]['puntos_hist'][-3:])
        racha_v = sum(stats[visita]['puntos_hist'][-3:])
        
        dif_g_l = sum(stats[local]['goles_f'][-3:]) - sum(stats[local]['goles_c'][-3:])
        dif_g_v = sum(stats[visita]['goles_f'][-3:]) - sum(stats[visita]['goles_c'][-3:])
        
        pts_tot_l = stats[local]['total_pts']
        pts_tot_v = stats[visita]['total_pts']

        
        features_lista.append({
            'Racha_Local': racha_l,
            'Racha_Visita': racha_v,
            'Dif_Goles_Local': dif_g_l,
            'Dif_Goles_Visita': dif_g_v,
            'Pts_Totales_Local': pts_tot_l,
            'Pts_Totales_Visita': pts_tot_v,
            'FTR': resultado, 
            'B365H': fila['B365H'], 
            'B365D': fila['B365D'],
            'B365A': fila['B365A']
        })


        if resultado == 'H':
            stats[local]['puntos_hist'].append(3); stats[visita]['puntos_hist'].append(0)
            stats[local]['total_pts'] += 3
        elif resultado == 'A':
            stats[local]['puntos_hist'].append(0); stats[visita]['puntos_hist'].append(3)
            stats[visita]['total_pts'] += 3
        else:
            stats[local]['puntos_hist'].append(1); stats[visita]['puntos_hist'].append(1)
            stats[local]['total_pts'] += 1; stats[visita]['total_pts'] += 1

        stats[local]['goles_f'].append(goles_l); stats[local]['goles_c'].append(goles_v)
        stats[visita]['goles_f'].append(goles_v); stats[visita]['goles_c'].append(goles_l)

    df_final = pd.DataFrame(features_lista)
    df_final.to_csv('dataset_final_ml.csv', index=False)
    logging.info(f"Éxito: Se generó 'dataset_final_ml.csv' con {len(df_final)} partidos.")

if __name__ == "__main__":
    generar_dataset_ml()
    