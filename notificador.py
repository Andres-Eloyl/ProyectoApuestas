import requests
import os

class BotPredictscore:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    # --- NUEVA FUNCIÓN UNIVERSAL ---
    def enviar_mensaje(self, mensaje_texto):
        """Recibe cualquier texto ya formateado y lo dispara a Telegram"""
        payload = {
            "chat_id": self.chat_id,
            "text": mensaje_texto
            # Nota: Quitamos el parse_mode="HTML" para que no dé error con los asteriscos **
        }
        
        try:
            respuesta = requests.post(self.url, data=payload)
            
            if respuesta.status_code == 200:
                print(f"✅ Notificación enviada a Telegram con éxito.")
            else:
                print(f"❌ Telegram rebotó el mensaje. Razón: {respuesta.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión de red: {e}")