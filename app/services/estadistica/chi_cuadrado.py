import numpy as np
import scipy.stats as stats
import pandas as pd
from collections import Counter


def _generar_curva_chi2(df: int, chi2_stat: float, alfa: float):
    """Genera los puntos para el gráfico asimétrico de Ji-Cuadrado."""
    crit_val = stats.chi2.ppf(1 - alfa, df)
    # Calculamos hasta dónde dibujar (un poco más allá del valor crítico o del estadístico)
    max_x = max(chi2_stat, stats.chi2.ppf(0.99, df)) + 2.0

    # Empezamos en 0.1 para evitar el infinito (asíntota) cuando df=1
    rango_x = np.linspace(0.1, max_x, 100)
    rango_y = stats.chi2.pdf(rango_x, df)

    puntos_curva = list()
    for vx, vy in zip(rango_x, rango_y):
        puntos_curva.append({"x": round(float(vx), 4), "y": round(float(vy), 4)})

    puntos_aceptacion = [p for p in puntos_curva if p['x'] <= crit_val]
    puntos_rechazo = [p for p in puntos_curva if p['x'] > crit_val]

    return puntos_curva, puntos_aceptacion, puntos_rechazo, crit_val


def calcular_chi2_bondad(datos: list, esperadas: list = None, tipo_ingreso: str = "frecuencias", alfa: float = 0.05,
                         contexto: str = "Categorías") -> dict:
    """Prueba Ji-Cuadrado de Bondad de Ajuste (1 Variable)."""

    # 1. Inteligencia de Datos: ¿Sueltos o Frecuencias?
    if tipo_ingreso == "datos_sueltos":
        conteo = Counter(datos)
        obs = list(conteo.values())
        cats = list(conteo.keys())
    else:
        # Ya vienen contados
        obs = [float(x) for x in datos]
        cats = [f"Cat {i + 1}" for i in range(len(obs))]

    n_cats = len(obs)
    if n_cats < 2: raise ValueError("Se necesitan al menos 2 categorías para comparar.")

    total_obs = sum(obs)

    # 2. Frecuencias Esperadas
    if not esperadas or len(esperadas) != n_cats:
        # Si no dan esperadas, asumimos Equiprobabilidad (todos deberían ser iguales)
        esp = [total_obs / n_cats] * n_cats
        msg_esp = f"Como no indicaste frecuencias esperadas, asumimos que todas las categorías deberían ser iguales ({round(esp[0], 2)})."
    else:
        # Si las dan en porcentajes o proporciones, las convertimos a frecuencias reales
        total_esp_input = sum(esperadas)
        esp = [(e / total_esp_input) * total_obs for e in esperadas]
        msg_esp = "Usamos las proporciones esperadas que ingresaste para calcular cuántos casos 'deberían' caer en cada categoría."

    # 3. Cálculo Estadístico
    chi2_stat, p_val = stats.chisquare(f_obs=obs, f_exp=esp)
    df = n_cats - 1

    # 4. Generar Curva
    p_curva, p_acep, p_rech, crit_val = _generar_curva_chi2(df, chi2_stat, alfa)

    rechazo = p_val < alfa
    decision = "RECHAZAMOS" if rechazo else "NO RECHAZAMOS"

    # Fórmulas LaTeX didácticas (solo mostramos las 2 primeras sumas para no romper la pantalla)
    str_suma = f"\\frac{{({obs[0]} - {round(esp[0], 1)})^2}}{{{round(esp[0], 1)}}}"
    if n_cats > 1:
        str_suma += f" + \\frac{{({obs[1]} - {round(esp[1], 1)})^2}}{{{round(esp[1], 1)}}}"
    if n_cats > 2:
        str_suma += " + \\dots"

    return {
        "tema": "Ji-Cuadrado (Bondad de Ajuste)",
        "contexto": contexto,
        "simbolo_estadistico": "\\chi^2",
        "datos_curva": p_curva, "sombreado_1": p_acep, "sombreado_2": p_rech,
        "paciente_x": round(chi2_stat, 2), "paciente_z": 0.0, "percentil": alfa * 100, "tipo_area": "cola_der",
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Frecuencias Observadas (O) vs Esperadas (E)",
                "explicacion": msg_esp,
                "formula_latex": f"\\text{{Total }}: {total_obs} \\quad gl = k - 1 = {n_cats} - 1 = {df}"
            },
            {
                "paso_num": 2,
                "titulo": "Cálculo del Estadístico (χ²)",  # <-- Unicode χ²
                "explicacion": "Calculamos la diferencia entre lo que observamos y lo que esperábamos, lo elevamos al cuadrado (para quitar negativos) y lo dividimos por lo esperado.",
                "formula_latex": f"\\chi^2 = \\Sigma \\frac{{(O - E)^2}}{{E}} = {str_suma} = {round(chi2_stat, 3)}"
            },
            {
                "paso_num": 3,
                "titulo": "Valor Crítico y Valor P",
                "explicacion": f"Buscamos la frontera de la zona de rechazo en la tabla Ji-Cuadrado con {df} grados de libertad y un alfa (α) de {alfa}.",
                "formula_latex": f"\\chi^2_{{crit}} = {round(crit_val, 3)} \\quad \\text{{Valor P}} = {round(p_val, 4)}"
            }
        ],
        "resultado_final": round(p_val, 4),
        "interpretacion": f"Como el p-valor ({round(p_val, 4)}) es {'menor' if rechazo else 'mayor'} que alfa (α), {decision} H₀. Las frecuencias observadas {'NO se ajustan' if rechazo else 'SÍ se ajustan'} a las esperadas."
    }

def calcular_chi2_independencia(matriz: list, raw_x: list = None, raw_y: list = None, tipo_ingreso: str = "tabla",
                                alfa: float = 0.05, contexto: str = "Variables") -> dict:
    """Prueba Ji-Cuadrado de Independencia (2 Variables)."""

    # 1. Inteligencia de Datos: ¿Tabla 2D o Columnas Sueltas?
    if tipo_ingreso == "datos_sueltos" and raw_x and raw_y:
        if len(raw_x) != len(raw_y): raise ValueError("X e Y deben tener la misma cantidad de datos.")
        # Pandas hace la magia de armar la tabla de contingencia al instante
        df_crosstab = pd.crosstab(pd.Series(raw_x), pd.Series(raw_y))
        obs_matrix = df_crosstab.values.tolist()
        msg_ingreso = f"Analizamos los {len(raw_x)} pares de datos y armamos una tabla de {len(obs_matrix)}x{len(obs_matrix[0])}."
    else:
        obs_matrix = matriz
        msg_ingreso = f"Utilizamos la tabla de {len(obs_matrix)} filas por {len(obs_matrix[0])} columnas que ingresaste."

    # 2. Cálculo Estadístico con Scipy
    chi2_stat, p_val, df, expected = stats.chi2_contingency(obs_matrix)

    # 3. Generar Curva Visual
    p_curva, p_acep, p_rech, crit_val = _generar_curva_chi2(df, chi2_stat, alfa)

    rechazo = p_val < alfa
    decision = "RECHAZAMOS" if rechazo else "NO RECHAZAMOS"

    return {
        "tema": "Ji-Cuadrado (Independencia)",
        "contexto": contexto,
        "simbolo_estadistico": "\\chi^2",
        "datos_curva": p_curva, "sombreado_1": p_acep, "sombreado_2": p_rech,
        "paciente_x": round(chi2_stat, 2), "paciente_z": 0.0, "percentil": alfa * 100, "tipo_area": "cola_der",
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Armar la Tabla y Grados de Libertad",
                "explicacion": f"{msg_ingreso} Para saber qué curva usar, calculamos los grados de libertad: (filas - 1) * (columnas - 1).",
                "formula_latex": f"gl = (f-1)(c-1) = {df}"
            },
            {
                "paso_num": 2,
                "titulo": "Frecuencias Esperadas (E)",
                "explicacion": "Si ambas variables fueran 100% independientes, ¿cuánta gente caería en cada celda? El sistema calcula esto multiplicando los totales de cada fila por los de cada columna.",
                "formula_latex": "E = \\frac{\\text{Total Fila} \\cdot \\text{Total Columna}}{\\text{Gran Total}}"
            },
            {
                "paso_num": 3,
                "titulo": "El Estadístico (χ²) y Decisión",  # <-- Unicode χ²
                "explicacion": "Comparamos la tabla Observada contra la tabla Esperada. Si la diferencia es inmensa, el número crece y cae en la zona roja de rechazo.",
                "formula_latex": f"\\chi^2 = {round(chi2_stat, 3)} \\quad \\chi^2_{{crit}} = {round(crit_val, 3)} \\quad P = {round(p_val, 4)}"
            }
        ],
        "resultado_final": round(p_val, 4),
        "interpretacion": f"{decision} H₀. Con un alfa (α) de {alfa}, la evidencia sugiere que las variables {'ESTÁN ASOCIADAS (Dependen una de otra)' if rechazo else 'SON INDEPENDIENTES'}."
    }