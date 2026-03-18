import numpy as np
import scipy.stats as stats


def calcular_puntaje_z_y_curva(media: float, desviacion: float, x: float, tipo_area: str = "menor", x2: float = None,
                               contexto: str = "Puntaje") -> dict:
    if desviacion <= 0: raise ValueError("La Desviación Estándar debe ser mayor a cero.")

    # 1. Calculamos el primer Z
    z = (x - media) / desviacion
    z_abs = abs(z)

    # 2. Generamos la curva completa
    z_rango = np.linspace(-4, 4, 100)
    x_rango = z_rango * desviacion + media
    y_rango = stats.norm.pdf(z_rango, 0, 1)

    puntos_curva = list()
    for vx, vy in zip(x_rango, y_rango):
        puntos_curva.append({"x": round(float(vx), 4), "y": round(float(vy), 4)})

    puntos_sombreados_1 = list()
    puntos_sombreados_2 = list()
    area_prob = 0.0

    # Variables dinámicas para la didáctica
    pasos_didacticos = list()
    z2 = None

    if tipo_area == "entre_dos_valores" and x2 is not None:
        z2 = (x2 - media) / desviacion
        x_min, x_max = min(x, x2), max(x, x2)
        z_min, z_max = min(z, z2), max(z, z2)

        area_prob = stats.norm.cdf(z_max) - stats.norm.cdf(z_min)
        puntos_sombreados_1 = [p for p in puntos_curva if x_min <= p['x'] <= x_max]

        pasos_didacticos = [
            {
                "paso_num": 1, "titulo": "Estandarizar ambos puntajes",
                "explicacion": "Convertimos los dos puntajes a Puntajes Z para ubicarlos en la curva normal estándar.",
                "formula_latex": f"Z_1 = \\frac{{{x_min} - {media}}}{{{desviacion}}} = {round(z_min, 2)} \\quad \\text{{y}} \\quad Z_2 = \\frac{{{x_max} - {media}}}{{{desviacion}}} = {round(z_max, 2)}"
            },
            {
                "paso_num": 2, "titulo": "Buscar las áreas acumuladas",
                "explicacion": "Buscamos en la tabla qué porcentaje de gente está por debajo de Z₂ y qué porcentaje está por debajo de Z₁.",
                "formula_latex": f"P(Z \\le {round(z_max, 2)}) = {round(stats.norm.cdf(z_max), 4)} \\quad \\text{{y}} \\quad P(Z \\le {round(z_min, 2)}) = {round(stats.norm.cdf(z_min), 4)}"
            },
            {
                "paso_num": 3, "titulo": "Restar las áreas (El espacio del medio)",
                "explicacion": "Al área más grande le restamos el área más pequeña para obtener exactamente el porcentaje que quedó atrapado entre ambos.",
                "formula_latex": f"P({x_min} \\le X \\le {x_max}) = {round(stats.norm.cdf(z_max), 4)} - {round(stats.norm.cdf(z_min), 4)} = {round(area_prob, 4)}"
            }
        ]
    else:
        # Lógica para los 4 modos anteriores (Un solo Z)
        if tipo_area == "menor":
            area_prob = stats.norm.cdf(z)
            puntos_sombreados_1 = [p for p in puntos_curva if p['x'] <= x]
            tit, exp, form = "Área a la Izquierda (Menor)", "Probabilidad de obtener un puntaje igual o menor.", f"P(X \\le {x}) = P(Z \\le {round(z, 2)}) = {round(area_prob, 4)}"
        elif tipo_area == "mayor":
            area_prob = 1 - stats.norm.cdf(z)
            puntos_sombreados_1 = [p for p in puntos_curva if p['x'] >= x]
            tit, exp, form = "Área a la Derecha (Mayor)", "A 1 (el 100%) le restamos el área menor.", f"P(X > {x}) = 1 - P(Z \\le {round(z, 2)}) = {round(area_prob, 4)}"
        elif tipo_area == "entre_media":
            area_prob = abs(stats.norm.cdf(z) - 0.5)
            puntos_sombreados_1 = [p for p in puntos_curva if min(media, x) <= p['x'] <= max(media, x)]
            tit, exp, form = "Área Central", "Distancia probabilística entre el centro y el paciente.", f"P({min(media, x)} \\le X \\le {max(media, x)}) = {round(area_prob, 4)}"
        elif tipo_area == "dos_colas":
            area_prob = 2 * stats.norm.cdf(-z_abs)
            puntos_sombreados_1 = [p for p in puntos_curva if p['x'] <= media - z_abs * desviacion]
            puntos_sombreados_2 = [p for p in puntos_curva if p['x'] >= media + z_abs * desviacion]
            tit, exp, form = "Área en los Extremos (Dos Colas)", "Probabilidad de hallar pacientes tan extremos (arriba o abajo).", f"P(Z \\le -{round(z_abs, 2)}) + P(Z \\ge {round(z_abs, 2)}) = {round(area_prob, 4)}"
        else:
            tit, exp, form = "", "", ""

        pasos_didacticos = [
            {
                "paso_num": 1, "titulo": "Estandarizar (Calcular Z)",
                "explicacion": f"Convertimos el puntaje X = {x} a Z.",
                "formula_latex": f"Z = \\frac{{{x} - {media}}}{{{desviacion}}} = {round(z, 2)}"
            },
            {
                "paso_num": 2, "titulo": tit, "explicacion": exp, "formula_latex": form
            }
        ]

    percentil = area_prob * 100

    return {
        "tema": "Probabilidades bajo la Curva Normal",
        "contexto": contexto,
        "simbolo_estadistico": "Z",
        "datos_curva": puntos_curva,
        "sombreado_1": puntos_sombreados_1,
        "sombreado_2": puntos_sombreados_2,
        "paciente_x": x,
        "paciente_z": round(z, 2),
        "paciente_x2": x2,
        "paciente_z2": round(z2, 2) if z2 is not None else None,
        "percentil": round(percentil, 2),  # <--- ¡ESTA ES LA LÍNEA QUE FALTABA!
        "tipo_area": tipo_area,
        "pasos": pasos_didacticos,
        "resultado_final": round(area_prob, 4),
        "interpretacion": f"El área sombreada representa el {round(percentil, 2)}% de la población."
    }