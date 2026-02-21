import requests

API_KEY = "5749c8a9d8882209e480dba0c542e21f"

SPORT = "soccer_spain_la_liga" 
REGIONS = "eu" 
MARKETS = "h2h" 

def probar_api_cuotas():
    print("Conectando con The Odds API...")
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}"
    
    try:
        respuesta = requests.get(url)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            print(f"✅ ¡Éxito! Se descargaron {len(datos)} partidos próximos.\n")
            
            if len(datos) > 0:
                partido = datos[0]
                equipo_local = partido['home_team']
                equipo_visita = partido['away_team']
                
                print(f"⚽ PRÓXIMO PARTIDO: {equipo_local} vs {equipo_visita}")
                print(f"📅 Fecha de inicio: {partido['commence_time']}")
                
                if partido['bookmakers']:
                    casa = partido['bookmakers'][0] 
                    print(f"🏦 Casa de Apuestas: {casa['title']}")
                    
                    mercado = casa['markets'][0]
                    print("   Cuotas actuales:")
                    for cuota in mercado['outcomes']:
                        print(f"      - {cuota['name']}: {cuota['price']}")
        else:
            print(f"❌ Error de la API: {respuesta.text}")
            
    except Exception as e:
        print(f"❌ Error de red: {e}")

if __name__ == "__main__":
    probar_api_cuotas()
