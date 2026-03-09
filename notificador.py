import os
import requests
from dotenv import load_dotenv

# Carga las claves secretas desde tu archivo .env
load_dotenv()


class BotPredictscore:
    def __init__(self) -> None:
        self.token = os.environ.get("TELEGRAM_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def enviar_mensaje(self, mensaje_texto: str) -> None:
        payload = {"chat_id": self.chat_id, "text": mensaje_texto}
        try:
            respuesta = requests.post(self.url, data=payload)
            if respuesta.status_code == 200:
                print("Notificación enviada a Telegram con éxito.")
            else:
                print(f"Telegram rebotó el mensaje. Razón: {respuesta.text}")
        except Exception as e:
            print(f"Error de conexión de red: {e}")
