import cartelera_automatica
cartelera_automatica.generar_cartelera_diaria()
import pandas as pd
try:
    df = pd.read_csv('partidos_hoy.csv')
    print("MATCHES GENERATED:", len(df))
    if not df.empty:
        print(df[['HomeTeam', 'AwayTeam']].head())
except Exception as e:
    print("FAILED:", e)
