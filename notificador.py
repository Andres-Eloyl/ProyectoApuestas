import requests
import os

class BotPredictscore:
    def __init__(self):
        self.token = os.environ.get("8117852326:AAFaZAf2rQkDbPWsBVlvHpwi_vQ31AcrJaQ")
        self.chat_id = os.environ.get("6275073288")
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def enviar_alerta_valor(self, local, visita, prob_local, cuota, ev):
        """Formatea y envía una predicción real a Telegram"""
        mensaje = (
            f"🚨 <b>ALERTA DE VALOR: PREDICTSCORE</b> 🚨\n\n"
            f"⚽ <b>{local} vs {visita}</b>\n"
            f"📊 Probabilidad IA (Local): <b>{prob_local:.1%}</b>\n"
            f"🏦 Cuota Casa de Apuestas: <b>{cuota}</b>\n"
            f"📈 <b>Valor Esperado (EV): {ev:.2f}</b>\n\n"
            f"💡 <i>Recomendación: Cuota ineficiente detectada. Oportunidad de inversión a largo plazo.</i>"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": mensaje,
            "parse_mode": "HTML"
        }
        
        try:
            respuesta = requests.post(self.url, data=payload)
            
            if respuesta.status_code == 200:
                print(f"✅ Notificación enviada a Telegram: {local} vs {visita}")
            else:
                print(f"❌ Telegram rebotó el mensaje. Razón: {respuesta.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión de red: {e}")