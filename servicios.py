import os
import json
import pandas as pd
from functools import lru_cache
import subprocess
import sys
import threading

class PredictionService:
    """Clase estática para agrupar las lecturas de DF y cacheo del Backend."""
    
    _lock = threading.Lock()
    _sync_en_progreso = False
    
    @classmethod
    @lru_cache(maxsize=1)
    def obtener_auditoria(cls) -> list:
        """Cachea y retorna la lectura bruta de json de historial_auditoria."""
        if not os.path.exists("historial_auditoria.json"):
            return []
        with open("historial_auditoria.json", "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    @lru_cache(maxsize=1)
    def obtener_historial_apuestas(cls) -> pd.DataFrame:
        """Retorna el DataFrame de apuetas o uno vacío. (Cacheado)"""
        if not os.path.exists("historial_apuestas.csv"):
            return pd.DataFrame()
        return pd.read_csv("historial_apuestas.csv")

    @classmethod
    def invalidar_cache(cls):
        """Limpia las lecturas a disco en memoria."""
        cls.obtener_auditoria.cache_clear()
        cls.obtener_historial_apuestas.cache_clear()
        
    @classmethod
    def sincronizar_predicciones_async(cls):
        """Lanza el workflow en background sin colgar Flask."""
        def tarea_background():
            with cls._lock:
                cls._sync_en_progreso = True
                try:
                    subprocess.run([sys.executable, "cartelera_automatica.py"], check=True)
                    subprocess.run([sys.executable, "predicciones_hoy.py"], check=True)
                    cls.invalidar_cache() # Las nuevas predicciones ya están en disco
                except Exception as e:
                    print(f"Error en tarea background: {e}")
                finally:
                    cls._sync_en_progreso = False

        if not cls._sync_en_progreso:
            hilo = threading.Thread(target=tarea_background)
            hilo.start()
            return True
        return False
