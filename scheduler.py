import schedule
import time
import logging
from alerta_telegram import analizar_y_notificar

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def job() -> None:
    logging.info("Ejecutando proceso de notificación programado...")
    try:
        analizar_y_notificar()
    except Exception as e:
        logging.error(f"Error durante la ejecución del job de Telegram: {e}")


def run_scheduler() -> None:
    # Envíos 3 veces al día
    schedule.every().day.at("08:00").do(job)
    schedule.every().day.at("14:00").do(job)
    schedule.every().day.at("20:00").do(job)

    logging.info(
        "Scheduler de Telegram iniciado. Envíos programados para: 08:00, 14:00 y 20:00"
    )

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
