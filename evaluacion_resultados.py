import pandas as pd
import os
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

HISTORIAL_FILE = "historial_apuestas.csv"


class EvaluadorResultados:
    @staticmethod
    def registrar_prediccion(
        fecha: str,
        local: str,
        visita: str,
        cuota: float,
        prob: float,
        ev: float,
        kelly: float,
        recomendacion: str,
        goles_l: Optional[float] = None,
        goles_v: Optional[float] = None,
        marcador: Optional[str] = None,
    ) -> None:
        """
        Registra la predicción en el historial para posterior evaluación.

        Args:
            fecha (str): Fecha del evento.
            local (str): Equipo local.
            visita (str): Equipo visitante.
            cuota (float): Cuota de la casa de apuestas.
            prob (float): Probabilidad calculada.
            ev (float): Expected Value.
            kelly (float): Fracción de Kelly sugerida.
            recomendacion (str): 'H', 'D', 'A' o 'No Bet'.
            goles_l (float, optional): xG Local.
            goles_v (float, optional): xG Visitante.
            marcador (str, optional): Marcador exacto predicho.
        """
        nueva_fila = pd.DataFrame(
            [
                {
                    "Fecha_Prediccion": datetime.now().strftime("%Y-%m-%d"),
                    "Fecha_Partido": fecha,
                    "HomeTeam": local,
                    "AwayTeam": visita,
                    "Cuota": cuota,
                    "Probabilidad": prob,
                    "EV": ev,
                    "Kelly_Stake": kelly,
                    "Recomendacion": recomendacion,  # ej. 'H', 'A', 'D' o 'No Bet'
                    "Proj_Goles_L": goles_l,
                    "Proj_Goles_V": goles_v,
                    "Marcador_Exacto": marcador,
                    "Resultado_Real": None,
                    "Ganancia_Perdida": 0.0,
                }
            ]
        )

        if os.path.exists(HISTORIAL_FILE):
            df = pd.read_csv(HISTORIAL_FILE)
            # Evitar duplicados del mismo partido
            if not (
                (df["Fecha_Partido"] == fecha)
                & (df["HomeTeam"] == local)
                & (df["AwayTeam"] == visita)
            ).any():
                df = pd.concat([df, nueva_fila], ignore_index=True)
                df.to_csv(HISTORIAL_FILE, index=False)
        else:
            nueva_fila.to_csv(HISTORIAL_FILE, index=False)

    @staticmethod
    def conciliar_resultados() -> None:
        """Cruza el historial_apuestas con partidos_procesados para comprobar los aciertos."""
        if not os.path.exists(HISTORIAL_FILE):
            logging.info("No hay historial de apuestas para conciliar.")
            return

        df_historial = pd.read_csv(HISTORIAL_FILE)

        # Prevenir error al asignar strings a columnas vacías parseadas como float64
        if "Resultado_Real" in df_historial.columns:
            df_historial["Resultado_Real"] = df_historial["Resultado_Real"].astype(
                object
            )
        try:
            df_reales = pd.read_csv("partidos_procesados.csv")
        except FileNotFoundError:
            logging.error("No se encontró partidos_procesados.csv.")
            return

        # Cruce de datos por equipo local y visitante (y fecha aprox si es necesario)
        match_column = "Resultado_Real"

        for idx, apuesta in df_historial.iterrows():
            if pd.isna(apuesta[match_column]) and apuesta["Recomendacion"] != "No Bet":
                # Buscar en los resultados reales
                partido = df_reales[
                    (df_reales["HomeTeam"] == apuesta["HomeTeam"])
                    & (df_reales["AwayTeam"] == apuesta["AwayTeam"])
                ]

                if not partido.empty:
                    # Coge el ultimo si hay varios recientes
                    resultado = partido.iloc[-1]["FTR"]
                    # Consideramos que la apuesta recomendada fue a Gana Local (H) por simplicidad
                    # Si la recom era H y resultado es H, ganó.
                    if apuesta["Recomendacion"] == "H":
                        if resultado == "H":
                            ganancia = (
                                (apuesta["Cuota"] - 1) * apuesta["Kelly_Stake"] * 100
                            )  # base 100
                        else:
                            ganancia = -apuesta["Kelly_Stake"] * 100
                    else:
                        ganancia = 0.0  # Extension future

                    df_historial.at[idx, "Resultado_Real"] = resultado
                    df_historial.at[idx, "Ganancia_Perdida"] = ganancia

        df_historial.to_csv(HISTORIAL_FILE, index=False)
        logging.info("Historial de apuestas conciliado.")

    @staticmethod
    def obtener_metricas() -> Dict[str, Any]:
        """
        Genera un diccionario con las métricas actuales del sistema.

        Returns:
            Dict[str, Any]: Aciertos, Fallos, WinRate, ROI, Yield, Beneficio_Total.
        """
        if not os.path.exists(HISTORIAL_FILE):
            return {
                "Aciertos": 0,
                "Fallos": 0,
                "WinRate": 0,
                "ROI": 0,
                "Yield": 0,
                "Beneficio_Total": 0,
            }

        df = pd.read_csv(HISTORIAL_FILE)
        df_evaluables = df.dropna(subset=["Resultado_Real"])
        df_evaluables = df_evaluables[df_evaluables["Recomendacion"] != "No Bet"]

        if df_evaluables.empty:
            return {
                "Aciertos": 0,
                "Fallos": 0,
                "WinRate": 0,
                "ROI": 0,
                "Yield": 0,
                "Beneficio_Total": 0,
            }

        aciertos = len(df_evaluables[df_evaluables["Ganancia_Perdida"] > 0])
        fallos = len(df_evaluables[df_evaluables["Ganancia_Perdida"] < 0])
        total = aciertos + fallos

        inversion_total = df_evaluables["Kelly_Stake"].sum() * 100
        beneficio_total = df_evaluables["Ganancia_Perdida"].sum()

        win_rate = (aciertos / total) * 100 if total > 0 else 0
        yield_pct = (
            (beneficio_total / inversion_total) * 100 if inversion_total > 0 else 0
        )

        return {
            "Aciertos": aciertos,
            "Fallos": fallos,
            "WinRate": round(win_rate, 2),
            "ROI": round(
                yield_pct, 2
            ),  # En apuestas el ROI y Yield suelen ser intercambiables, pero se usa Yield para medir rentabilidad sobre apostado.
            "Yield": round(yield_pct, 2),
            "Beneficio_Total": round(beneficio_total, 2),
        }


if __name__ == "__main__":
    EvaluadorResultados.conciliar_resultados()
    print(EvaluadorResultados.obtener_metricas())
