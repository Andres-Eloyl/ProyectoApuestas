import os
import requests
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

# Credenciales Telegram
# Reemplaza con tu Token y Chat ID, o expónlas como variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "TU_TOKEN_AQUI")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "TU_CHAT_ID_AQUI")


def enviar_mensaje_telegram(mensaje: str) -> bool:
    """Envía un mensaje formateado al chat de Telegram especificado."""
    if TELEGRAM_TOKEN == "TU_TOKEN_AQUI" or TELEGRAM_CHAT_ID == "TU_CHAT_ID_AQUI":
        logging.warning(
            "⚠️ Credenciales de Telegram no configuradas. Usa variables de entorno o edita alerta_telegram.py"
        )
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "MarkdownV2"}

    try:
        respuesta = requests.post(url, json=payload)
        if respuesta.status_code == 200:
            logging.info("✅ Alerta de Telegram enviada exitosamente.")
            return True
        else:
            logging.error(
                f"❌ Error al enviar Telegram (Http {respuesta.status_code}): {respuesta.text}"
            )
            return False
    except Exception as e:
        logging.error(f"❌ Excepción al contactar con la API de Telegram: {e}")
        return False


def escape_markdown(text: str) -> str:
    """Escapa caracteres reservados de MarkdownV2 para evitar errores en la API."""
    reservados = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in reservados:
        text = text.replace(char, f"\\{char}")
    return text


def analizar_y_notificar() -> None:
    """Lee las predicciones y genera un reporte Premium para Telegram."""

    if not os.path.exists("partidos_hoy.csv"):
        logging.warning("No se encontró partidos_hoy.csv, la cartelera está vacía.")
        return

    # Cargar predicciones del día
    try:
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        df_pred = pd.read_csv("historial_apuestas.csv")
        df_pred = df_pred[df_pred["Fecha_Prediccion"] == hoy_str]
    except Exception as e:
        logging.error(f"No se pudo cargar el historial de apuestas: {e}")
        return

    # Filtrar predicciones rentables y ordenar por EV descendente
    ev_picks = df_pred[df_pred["Recomendacion"] != "No Bet"].sort_values(
        "EV", ascending=False
    )

    momento = "☀️ Resumen Matutino"
    hora = datetime.now().hour
    if hora >= 12 and hora < 18:
        momento = "🌤️ Resumen de Tarde"
    elif hora >= 18:
        momento = "🌙 Resumen Nocturno"

    fecha = datetime.now().strftime("%d/%m/%Y")

    if ev_picks.empty:
        mensaje_base = f"""*PredictScore {momento}* 🤖⚽
*{fecha}*

Actualmente no hemos detectado _Picks de Valor \\(EV\\+\\)_ en las {len(df_pred)} proyecciones de hoy\\. 

El Oráculo se mantiene a la espera de mejores cuotas o nuevas jornadas\\.🛡️

🔗 [Visitar PredictScore Dashboard](http://127.0.0.1:5000/)"""
        enviar_mensaje_telegram(mensaje_base)
        return

    top_3 = ev_picks.head(3)

    picks_texto = ""
    for _, fila in top_3.iterrows():
        local = escape_markdown(fila["HomeTeam"])
        visita = escape_markdown(fila["AwayTeam"])
        cuota = escape_markdown(str(fila["Cuota"]))
        ev = escape_markdown(str(round(fila["EV"], 2)))
        marcador = escape_markdown(fila["Marcador_Exacto"])
        prob = escape_markdown(str(round(fila["Probabilidad"] * 100, 1)))

        picks_texto += f"🎯 *{local}* vs *{visita}*\n"
        picks_texto += f"   • Sugerencia: Local @ {cuota}\n"
        picks_texto += f"   • Prob\\. IA: {prob}%\n"
        picks_texto += f"   • EV \\(Valor\\): {ev}\n"
        picks_texto += f"   • Marcador Proyectado: {marcador}\n\n"

    mensaje = f"""*PredictScore {momento}* 📊🔥
*{fecha}*

Hemos escaneado {len(df_pred)} partidos y detectamos oportunidades rentables:

{picks_texto}

Para ver el desglose matemático profundo, estadísticas de Poisson y la gestión de riesgo completa, visita el Dashboard\\.

🔗 [Abrir Predictive Motor V3](http://127.0.0.1:5000/)"""

    enviar_mensaje_telegram(mensaje)


if __name__ == "__main__":
    logging.info("Ejecutando servicio de Alertas Telegram...")
    analizar_y_notificar()
