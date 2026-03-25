from  statsmodels.stats.power import TTestIndPower
import math

import scipy.stats as stats
import numpy as np


def calcular_poder_muestra(tipo_calculo: str, alfa: float, tipo_ingreso: str = "d_cohen", d_cohen: float = None,
                           mu0: float = None, mu1: float = None, sigma: float = None, n: float = None,
                           poder: float = None, contexto: str = "Estudio") -> dict:
    if not (0 < alfa < 1): raise ValueError("Alfa (α) debe estar entre 0 y 1 (Ej: 0.05).")

    pasos_didacticos = []

    # ==========================================
    # 1. LA MAGIA DIDÁCTICA: ¿De dónde sale 'd'?
    # ==========================================
    if tipo_ingreso == "medias_reales":
        if sigma is None or sigma <= 0: raise ValueError("La desviación estándar (σ) debe ser mayor a 0.")
        if mu0 is None or mu1 is None: raise ValueError("Debes ingresar ambas medias (μ₀ y μ₁).")

        d_real = abs(mu1 - mu0) / sigma
        pasos_didacticos.append({
            "paso_num": 1, "titulo": "Calcular el Tamaño del Efecto (d de Cohen)",
            "explicacion": f"Como ingresaste los valores reales del estudio, primero estandarizamos la diferencia. Restamos las medias y dividimos por la desviación estándar (σ = {sigma}).",
            "formula_latex": f"d = \\frac{{|{mu1} - {mu0}|}}{{{sigma}}} = {round(d_real, 3)}"
        })
    else:
        if d_cohen is None or d_cohen <= 0: raise ValueError("El tamaño del efecto (d) debe ser mayor a 0.")
        d_real = d_cohen
        pasos_didacticos.append({
            "paso_num": 1, "titulo": "Definir el Tamaño del Efecto",
            "explicacion": f"Asumimos directamente un tamaño del efecto estandarizado de d = {d_real}.",
            "formula_latex": f"d = {d_real}"
        })

    # ==========================================
    # 2. RESOLVER LA ECUACIÓN (Statsmodels)
    # ==========================================
    analysis = TTestIndPower()

    if tipo_calculo == "calcular_n":
        if poder is None or not (0 < poder < 1): raise ValueError("El Poder debe estar entre 0 y 1 (Ej: 0.80).")
        n_calc = analysis.solve_power(effect_size=d_real, nobs1=None, alpha=alfa, power=poder, ratio=1.0,
                                      alternative='two-sided')
        n_final = math.ceil(n_calc)
        poder_final = poder
    else:
        if n is None or n < 2: raise ValueError("El tamaño de muestra (n) debe ser al menos 2.")
        poder_calc = analysis.solve_power(effect_size=d_real, nobs1=n, alpha=alfa, power=None, ratio=1.0,
                                          alternative='two-sided')
        poder_final = poder_calc
        n_final = int(n)

    beta = 1.0 - poder_final

    pasos_didacticos.append({
        "paso_num": 2, "titulo": "Establecer los Riesgos (α y β)",
        "explicacion": f"Fijamos el riesgo de falsos positivos en α = {alfa}. El Poder es (1 - β), la capacidad de evitar falsos negativos.",
        "formula_latex": f"\\alpha = {alfa} \\quad \\beta = {round(beta, 4)}"
    })

    if tipo_calculo == "calcular_n":
        pasos_didacticos.append({
            "paso_num": 3, "titulo": "Despejar el Tamaño de Muestra (n)",
            "explicacion": f"Para garantizar que atraparemos ese efecto el {round(poder_final * 100, 2)}% de las veces, necesitamos reclutar a {n_final} sujetos.",
            "formula_latex": f"n = {n_final} \\text{{ sujetos}}"
        })
        res_num = n_final
        interpretacion = f"Para lograr un Poder del {round(poder_final * 100, 2)}% con un efecto de {round(d_real, 3)} y un alfa de {alfa}, necesitas una muestra mínima de {n_final} personas por grupo."
    else:
        pasos_didacticos.append({
            "paso_num": 3, "titulo": "Calcular el Poder del Test (1 - β)",
            "explicacion": f"Con {n_final} sujetos, la probabilidad de que tu experimento detecte el efecto es del {round(poder_final * 100, 2)}%.",
            "formula_latex": f"1 - \\beta = {round(poder_final, 4)}"
        })
        res_num = round(poder_final, 4)
        interpretacion = f"Con {n_final} personas por grupo, tu test tiene un {round(poder_final * 100, 2)}% de probabilidad de detectar la diferencia. El riesgo de Error Tipo II (β) es del {round(beta * 100, 2)}%."

    # ==========================================
    # 3. GEOMETRÍA DE LAS DOS CAMPANAS
    # ==========================================
    ncp = d_real * math.sqrt(n_final / 2)
    z_critico = stats.norm.ppf(1 - alfa / 2)

    rango_x = np.linspace(-4, ncp + 4, 200)
    curva_h0_y = stats.norm.pdf(rango_x, 0, 1)
    curva_h1_y = stats.norm.pdf(rango_x, ncp, 1)

    puntos_h0 = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(rango_x, curva_h0_y)]
    puntos_h1 = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(rango_x, curva_h1_y)]

    sombreado_alfa = [p for p in puntos_h0 if p['x'] >= z_critico]
    sombreado_beta = [p for p in puntos_h1 if p['x'] <= z_critico]
    sombreado_poder = [p for p in puntos_h1 if p['x'] >= z_critico]

    return {
        "tema": "Análisis de Poder y Tamaño de Muestra",
        "contexto": contexto,
        "simbolo_estadistico": "Poder" if tipo_calculo == "calcular_poder" else "n",
        "datos_curva": puntos_h0,
        "datos_curva2": puntos_h1,
        "sombreado_1": sombreado_alfa,
        "sombreado_2": sombreado_beta,
        "sombreado_3": sombreado_poder,
        "paciente_x": round(float(z_critico), 2),
        "paciente_z": round(float(ncp), 2),
        "percentil": poder_final * 100,
        "tipo_area": tipo_calculo,
        "pasos": pasos_didacticos,
        "resultado_final": res_num,
        "interpretacion": interpretacion
    }