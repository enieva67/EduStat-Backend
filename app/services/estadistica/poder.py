from  statsmodels.stats.power import TTestIndPower
import math

import scipy.stats as stats
import numpy as np

def calcular_poder_muestra(tipo_calculo: str, d_cohen: float, alfa: float, n: float = None, poder: float = None,
                           contexto: str = "Estudio") -> dict:
    if d_cohen <= 0: raise ValueError("El tamaño del efecto (d de Cohen) debe ser mayor a 0.")
    if not (0 < alfa < 1): raise ValueError("Alfa (α) debe estar entre 0 y 1 (Ej: 0.05).")

    analysis = TTestIndPower()

    # 1. RESOLVER LA ECUACIÓN (Statsmodels hace la magia pesada)
    if tipo_calculo == "calcular_n":
        if poder is None or not (0 < poder < 1): raise ValueError("El Poder (1-β) debe estar entre 0 y 1 (Ej: 0.80).")
        # Calculamos n para 2 muestras independientes (ratio=1.0)
        n_calc = analysis.solve_power(effect_size=d_cohen, nobs1=None, alpha=alfa, power=poder, ratio=1.0,
                                      alternative='two-sided')
        n_final = math.ceil(n_calc)  # Las personas no se pueden partir a la mitad
        poder_final = poder
    else:
        if n is None or n < 2: raise ValueError("El tamaño de muestra (n) debe ser al menos 2.")
        # Calculamos el poder dado un n
        poder_calc = analysis.solve_power(effect_size=d_cohen, nobs1=n, alpha=alfa, power=None, ratio=1.0,
                                          alternative='two-sided')
        poder_final = poder_calc
        n_final = int(n)

    beta = 1.0 - poder_final

    # 2. GENERAR LA GEOMETRÍA DE LAS DOS CAMPANAS (Para enseñar visualmente)
    # H0 está centrada en 0. H1 está desplazada por el "Parámetro de No Centralidad" (NCP)
    ncp = d_cohen * math.sqrt(n_final / 2)

    z_critico = stats.norm.ppf(1 - alfa / 2)  # Valor crítico a dos colas (Ej: 1.96)

    # Creamos un eje X lo suficientemente largo para abarcar ambas campanas
    rango_x = np.linspace(-4, ncp + 4, 200)

    curva_h0_y = stats.norm.pdf(rango_x, 0, 1)  # Campana 1 (Nula)
    curva_h1_y = stats.norm.pdf(rango_x, ncp, 1)  # Campana 2 (Alternativa, desplazada)

    puntos_h0 = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(rango_x, curva_h0_y)]
    puntos_h1 = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(rango_x, curva_h1_y)]

    # 3. ZONIFICACIÓN DIDÁCTICA (Cortamos las campanas en pedazos)
    # Zona Roja (Alfa): Área de H0 que supera el valor crítico
    sombreado_alfa = [p for p in puntos_h0 if p['x'] >= z_critico]

    # Zona Gris (Beta): Área de H1 que cae ANTES del valor crítico (No lo detectamos)
    sombreado_beta = [p for p in puntos_h1 if p['x'] <= z_critico]

    # Zona Verde (Poder): Área de H1 que cae DESPUÉS del valor crítico (Sí lo detectamos)
    sombreado_poder = [p for p in puntos_h1 if p['x'] >= z_critico]

    # 4. TEXTOS DIDÁCTICOS SEGÚN LO QUE EL USUARIO QUERÍA CALCULAR
    if tipo_calculo == "calcular_n":
        paso_final = {
            "paso_num": 3, "titulo": "Despejar el Tamaño de Muestra (n)",
            "explicacion": f"Para garantizar que atraparemos ese efecto el {poder_final * 100}% de las veces, necesitamos reclutar a {n_final} sujetos por grupo.",
            "formula_latex": f"n = {n_final} \\text{{ sujetos}}"
        }
        res_num = n_final
        interpretacion = f"Para lograr un Poder del {round(poder_final * 100, 2)}% con un efecto de {d_cohen} y un alfa de {alfa}, necesitas una muestra mínima de {n_final} personas por grupo."
    else:
        paso_final = {
            "paso_num": 3, "titulo": "Calcular el Poder del Test (1 - β)",
            "explicacion": f"Con {n_final} sujetos, la probabilidad de que tu experimento detecte el efecto (si realmente existe) es del {round(poder_final * 100, 2)}%.",
            "formula_latex": f"1 - \\beta = {round(poder_final, 4)}"
        }
        res_num = round(poder_final, 4)
        interpretacion = f"Con {n_final} personas por grupo y un efecto de {d_cohen}, tu test tiene un {round(poder_final * 100, 2)}% de probabilidad de detectar la diferencia (Poder). El riesgo de Error Tipo II (β) es del {round(beta * 100, 2)}%."

    return {
        "tema": "Análisis de Poder y Tamaño de Muestra",
        "contexto": contexto,
        "simbolo_estadistico": "Poder" if tipo_calculo == "calcular_poder" else "n",

        # Mandamos DOS curvas y TRES sombreados al Frontend
        "datos_curva": puntos_h0,  # La usaremos para H0
        "datos_curva2": puntos_h1,  # La usaremos para H1
        "sombreado_1": sombreado_alfa,  # Rojo
        "sombreado_2": sombreado_beta,  # Gris
        "sombreado_3": sombreado_poder,  # Verde
        "paciente_x": z_critico,  # Línea de corte crítico
        "paciente_z": ncp,  # Distancia entre campanas
        "percentil": poder_final * 100,
        "tipo_area": tipo_calculo,

        "pasos": [
            {
                "paso_num": 1, "titulo": "Definir el Tamaño del Efecto (d de Cohen)",
                "explicacion": f"Asumimos que la diferencia real entre los grupos es de d = {d_cohen}. Esto separa teóricamente nuestras dos campanas (H₀ y H₁).",
                "formula_latex": f"d = {d_cohen}"
            },
            {
                "paso_num": 2, "titulo": "Establecer los Riesgos (α y β)",
                "explicacion": f"Fijamos el riesgo de falsos positivos (Error Tipo I) en α = {alfa}. El Poder es (1 - β), la capacidad de evitar falsos negativos.",
                "formula_latex": f"\\alpha = {alfa} \\quad \\beta = {round(beta, 4)}"
            },
            paso_final
        ],
        "resultado_final": res_num,
        "interpretacion": interpretacion
    }
