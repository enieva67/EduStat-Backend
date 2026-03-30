import math
import numpy as np
import scipy.stats as stats
from statsmodels.stats.proportion import proportions_ztest


def calcular_ttest_independiente(datos_a: list, datos_b: list, alfa: float = 0.05, tipo_prueba: str = "dos_colas",
                                 ctx_a: str = "Grupo A", ctx_b: str = "Grupo B") -> dict:
    if len(datos_a) < 2 or len(datos_b) < 2: raise ValueError("Cada grupo debe tener al menos 2 datos.")

    n1, n2 = len(datos_a), len(datos_b)
    mean1, mean2 = np.mean(datos_a), np.mean(datos_b)
    var1, var2 = np.var(datos_a, ddof=1), np.var(datos_b, ddof=1)

    # Diferencia de medias (Lo que graficaremos)
    diferencia_medias = mean1 - mean2

    # Prueba T de Welch (No asume varianzas iguales, es el estándar más seguro hoy en día)
    t_stat, p_val_2tails = stats.ttest_ind(datos_a, datos_b, equal_var=False)

    # Grados de libertad (Ecuación de Welch-Satterthwaite)
    df_num = (var1 / n1 + var2 / n2) ** 2
    df_den = ((var1 / n1) ** 2) / (n1 - 1) + ((var2 / n2) ** 2) / (n2 - 1)
    df = df_num / df_den

    # Lógica de colas para P-Valor y Críticos
    if tipo_prueba == "dos_colas":
        p_val = p_val_2tails
        crit_inf, crit_sup = stats.t.ppf(alfa / 2, df), stats.t.ppf(1 - alfa / 2, df)
        rechazo = t_stat <= crit_inf or t_stat >= crit_sup
        str_critico = f"\\pm {round(crit_sup, 3)}"
        h1_latex = "\\mu_1 - \\mu_2 \\neq 0"
    elif tipo_prueba == "cola_der":
        p_val = p_val_2tails / 2 if t_stat > 0 else 1 - (p_val_2tails / 2)
        crit_inf, crit_sup = -float('inf'), stats.t.ppf(1 - alfa, df)
        rechazo = t_stat >= crit_sup
        str_critico = f"{round(crit_sup, 3)}"
        h1_latex = "\\mu_1 - \\mu_2 > 0"
    else:  # cola_izq
        p_val = p_val_2tails / 2 if t_stat < 0 else 1 - (p_val_2tails / 2)
        crit_inf, crit_sup = stats.t.ppf(alfa, df), float('inf')
        rechazo = t_stat <= crit_inf
        str_critico = f"{round(crit_inf, 3)}"
        h1_latex = "\\mu_1 - \\mu_2 < 0"

    decision = "RECHAZAMOS" if rechazo else "NO RECHAZAMOS"

    # Generar curva visual T de Student CENTRADA EN CERO (Hipótesis Nula)
    rango_x = np.linspace(-4, 4, 100)
    rango_y = stats.t.pdf(rango_x, df)
    puntos_curva = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(rango_x, rango_y)]

    puntos_aceptacion = []
    puntos_rechazo_1 = []
    puntos_rechazo_2 = []

    for p in puntos_curva:
        if (tipo_prueba == "dos_colas" and p['x'] <= crit_inf) or (tipo_prueba == "cola_izq" and p['x'] <= crit_inf):
            puntos_rechazo_1.append(p)
        elif (tipo_prueba == "dos_colas" and p['x'] >= crit_sup) or (tipo_prueba == "cola_der" and p['x'] >= crit_sup):
            puntos_rechazo_2.append(p)
        else:
            puntos_aceptacion.append(p)

    return {
        "tema": "T de Student (Muestras Independientes)",
        "contexto": f"{ctx_a} vs {ctx_b}",
        "simbolo_estadistico": "P_val",
        "datos_curva": puntos_curva, "sombreado_1": puntos_aceptacion, "sombreado_2": puntos_rechazo_1,
        "sombreado_3": puntos_rechazo_2,
        "paciente_x": round(t_stat, 2), "paciente_z": 0.0, "percentil": alfa * 100, "tipo_area": tipo_prueba,
        "pasos": [
            {
                "paso_num": 1, "titulo": "Plantear Hipótesis (H₀ vs H₁)",
                "explicacion": f"Nuestra Hipótesis Nula (H₀) es que NO hay diferencia entre {ctx_a} y {ctx_b}. O sea, la resta de sus promedios es cero.",
                "formula_latex": f"H_0: \\mu_1 - \\mu_2 = 0 \\quad \\text{{vs}} \\quad H_1: {h1_latex}"
            },
            {
                "paso_num": 2, "titulo": "Calcular la Diferencia Muestral",
                "explicacion": f"El promedio del Grupo A es {round(mean1, 2)} y del Grupo B es {round(mean2, 2)}. Su diferencia real es {round(diferencia_medias, 2)}.",
                "formula_latex": f"\\bar{{X}}_1 - \\bar{{X}}_2 = {round(mean1, 2)} - {round(mean2, 2)} = {round(diferencia_medias, 2)}"
            },
            {
                "paso_num": 3, "titulo": "Estadístico T de Welch",
                "explicacion": f"Estandarizamos esa diferencia dividiéndola por el error estándar combinado (Usamos T de Welch que es más robusta porque asume varianzas distintas). Grados de libertad (gl) = {round(df, 1)}",
                "formula_latex": f"t_{{calc}} = {round(t_stat, 3)} \\quad t_{{crit}} = {str_critico}"
            }
        ],
        "resultado_final": round(p_val, 4),
        "interpretacion": f"Como P={round(p_val, 4)}, {decision} H₀. {'Existen' if rechazo else 'NO existen'} diferencias estadísticamente significativas entre los promedios de ambos grupos."
    }


def calcular_z_proporciones(exitos_a: int, n_a: int, exitos_b: int, n_b: int, alfa: float = 0.05,
                            tipo_prueba: str = "dos_colas", ctx_a: str = "Grupo A", ctx_b: str = "Grupo B") -> dict:
    if n_a < 1 or n_b < 1: raise ValueError("Las muestras deben ser mayores a 0.")
    if exitos_a > n_a or exitos_b > n_b: raise ValueError("Los éxitos no pueden superar al tamaño de la muestra.")

    counts = np.array([exitos_a, exitos_b])
    nobs = np.array([n_a, n_b])

    p1, p2 = exitos_a / n_a, exitos_b / n_b

    # statsmodels proportions_ztest
    alternative_map = {"dos_colas": "two-sided", "cola_der": "larger", "cola_izq": "smaller"}
    z_stat, p_val = proportions_ztest(counts, nobs, alternative=alternative_map[tipo_prueba])

    if tipo_prueba == "dos_colas":
        crit_inf, crit_sup = stats.norm.ppf(alfa / 2), stats.norm.ppf(1 - alfa / 2)
        rechazo = z_stat <= crit_inf or z_stat >= crit_sup
        str_critico = f"\\pm {round(crit_sup, 3)}"
        h1_latex = "P_1 - P_2 \\neq 0"
    elif tipo_prueba == "cola_der":
        crit_inf, crit_sup = -float('inf'), stats.norm.ppf(1 - alfa)
        rechazo = z_stat >= crit_sup
        str_critico = f"{round(crit_sup, 3)}"
        h1_latex = "P_1 - P_2 > 0"
    else:
        crit_inf, crit_sup = stats.norm.ppf(alfa), float('inf')
        rechazo = z_stat <= crit_inf
        str_critico = f"{round(crit_inf, 3)}"
        h1_latex = "P_1 - P_2 < 0"

    decision = "RECHAZAMOS" if rechazo else "NO RECHAZAMOS"

    # Curva Z normal estándar centrada en 0
    rango_x = np.linspace(-4, 4, 100)
    rango_y = stats.norm.pdf(rango_x, 0, 1)
    puntos_curva = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(rango_x, rango_y)]
    puntos_aceptacion, puntos_rechazo_1, puntos_rechazo_2 = [], [], []

    for p in puntos_curva:
        if (tipo_prueba == "dos_colas" and p['x'] <= crit_inf) or (tipo_prueba == "cola_izq" and p['x'] <= crit_inf):
            puntos_rechazo_1.append(p)
        elif (tipo_prueba == "dos_colas" and p['x'] >= crit_sup) or (tipo_prueba == "cola_der" and p['x'] >= crit_sup):
            puntos_rechazo_2.append(p)
        else:
            puntos_aceptacion.append(p)

    return {
        "tema": "Prueba Z para Dos Proporciones",
        "contexto": f"{ctx_a} vs {ctx_b}",
        "simbolo_estadistico": "P_val",
        "datos_curva": puntos_curva, "sombreado_1": puntos_aceptacion, "sombreado_2": puntos_rechazo_1,
        "sombreado_3": puntos_rechazo_2,
        "paciente_x": round(z_stat, 2), "paciente_z": 0.0, "percentil": alfa * 100, "tipo_area": tipo_prueba,
        "pasos": [
            {
                "paso_num": 1, "titulo": "Plantear Hipótesis (Proporciones)",
                "explicacion": f"H₀ asume que la tasa de éxito del {ctx_a} (P₁) es idéntica a la del {ctx_b} (P₂).",
                "formula_latex": f"H_0: P_1 = P_2 \\quad \\text{{vs}} \\quad H_1: {h1_latex}"
            },
            {
                "paso_num": 2, "titulo": "Proporciones Observadas",
                "explicacion": f"Grupo A: {exitos_a}/{n_a} éxitos. Grupo B: {exitos_b}/{n_b} éxitos.",
                "formula_latex": f"p_1 = {round(p1, 3)} \\quad p_2 = {round(p2, 3)}"
            },
            {
                "paso_num": 3, "titulo": "Estadístico Z",
                "explicacion": "Usamos la distribución Normal (Z) para comparar si la diferencia de tasas es suficientemente grande.",
                "formula_latex": f"Z_{{calc}} = {round(z_stat, 3)} \\quad Z_{{crit}} = {str_critico} \\quad P = {round(p_val, 4)}"
            }
        ],
        "resultado_final": round(p_val, 4),
        "interpretacion": f"Como P={round(p_val, 4)}, {decision} H₀. Las proporciones de ambos grupos {'DIFIEREN' if rechazo else 'SON SIMILARES'} estadísticamente."
    }


def calcular_mann_whitney(datos_a: list, datos_b: list, alfa: float = 0.05, tipo_prueba: str = "dos_colas",
                          ctx_a: str = "Grupo A", ctx_b: str = "Grupo B") -> dict:
    if len(datos_a) < 1 or len(datos_b) < 1: raise ValueError("Cada grupo debe tener al menos 1 dato.")

    # Mann-Whitney U Test (No Paramétrico)
    alternative_map = {"dos_colas": "two-sided", "cola_der": "greater", "cola_izq": "less"}
    u_stat, p_val = stats.mannwhitneyu(datos_a, datos_b, alternative=alternative_map[tipo_prueba])

    rechazo = p_val < alfa
    decision = "RECHAZAMOS" if rechazo else "NO RECHAZAMOS"

    return {
        "tema": "U de Mann-Whitney (No Paramétrico)",
        "contexto": f"{ctx_a} vs {ctx_b}",
        "simbolo_estadistico": "P_val",
        "datos_curva": None,  # En no paramétricos no solemos dibujar campanas
        "paciente_x": 0.0, "percentil": alfa * 100, "tipo_area": tipo_prueba,
        "pasos": [
            {
                "paso_num": 1, "titulo": "Lógica No Paramétrica (Rangos)",
                "explicacion": "A diferencia del T-Test, la U de Mann-Whitney no usa los valores reales, sino que mezcla todos los datos, los ordena de menor a mayor, y analiza los 'rangos' (posiciones).",
                "formula_latex": "\\text{Se calcula la suma de rangos } R_1 \\text{ y } R_2"
            },
            {
                "paso_num": 2, "titulo": "El Estadístico (U)",
                "explicacion": "La U representa el número de veces que un dato del Grupo A es mayor que un dato del Grupo B.",
                "formula_latex": f"U = {round(u_stat, 2)}"
            },
            {
                "paso_num": 3, "titulo": "Decisión (P-Valor)",
                "explicacion": f"Calculamos la probabilidad de obtener esta distribución de rangos al azar.",
                "formula_latex": f"P = {round(p_val, 4)}"
            }
        ],
        "resultado_final": round(p_val, 4),
        "interpretacion": f"{decision} H₀. Existen evidencias para decir que la distribución del {ctx_a} es {'DIFERENTE a' if rechazo else 'IGUAL a'} la del {ctx_b}."
    }