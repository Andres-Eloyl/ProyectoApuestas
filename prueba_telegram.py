import os
import requests
from dotenv import load_dotenv

# 1. Cargamos los secretos desde tu archivo .env local
load_dotenv()

# 2. Leemos las variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print("🔌 Intentando conectar con Telegram...")

# 3. Disparamos el mensaje
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
respuesta = requests.post(url, data={
    "chat_id": CHAT_ID, 
    "text": "¡Hola Andrés! 🚀 La conexión desde tu PC usando el archivo .env funciona perfectamente."
})

# 4. Diagnóstico
if respuesta.status_code == 200:
    print("✅ ¡ÉXITO! Revisa tu celular, el mensaje debió llegar.")
else:
    print(f"❌ ERROR {respuesta.status_code}: Telegram rebotó el mensaje.")
    print("Detalle:", respuesta.text)