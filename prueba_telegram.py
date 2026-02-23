import requests

# Pega aquí exactamente lo que tienes en tus Secrets de GitHub
TOKEN = "8117852326:AAFaZAf2rQkDbPWsBVlvHpwi_vQ31AcrJaQ" 
CHAT_ID = "6275073288"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "🚀 PRUEBA DIRECTA: Si lees esto, el Chat ID y el Token son correctos."
}

respuesta = requests.post(url, data=payload)
print("Respuesta de Telegram:", respuesta.json())