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


# --- NUEVA FUNCIÓN: PROCESO INVERSO ---

def calcular_x_desde_area(media: float, desviacion: float, area1: float, tipo_area: str = "menor", area2: float = None,
                          contexto: str = "Puntaje") -> dict:
    if desviacion <= 0: raise ValueError("La desviación debe ser mayor a cero.")

    # 1. Normalizar las áreas (el estudiante puede ingresar 95 o 0.95)
    p1 = area1 / 100.0 if area1 >= 1 else area1
    if not (0 < p1 < 1): raise ValueError("El área debe estar entre 0 y 100% (exclusivo).")

    z2 = None
    x2 = None
    p2 = None

    # 2. Encontrar Z usando la Función Inversa (ppf) y despejar X
    if tipo_area == "entre_dos_valores" and area2 is not None:
        p2 = area2 / 100.0 if area2 >= 1 else area2
        if not (0 < p2 < 1): raise ValueError("El área 2 debe estar entre 0 y 100%.")

        p_min, p_max = min(p1, p2), max(p1, p2)
        z_min, z_max = stats.norm.ppf(p_min), stats.norm.ppf(p_max)

        x_min = media + (z_min * desviacion)
        x_max = media + (z_max * desviacion)

        z, x_val = z_min, x_min
        z2, x2 = z_max, x_max
        area_prob = p_max - p_min

        pasos_didacticos = [
            {
                "paso_num": 1, "titulo": "Buscar Z en la Tabla Inversa",
                "explicacion": f"Buscamos qué Puntajes Z acumulan el {round(p_min * 100, 2)}% y el {round(p_max * 100, 2)}% de la campana.",
                "formula_latex": f"Z_1 = {round(z_min, 3)} \\quad \\text{{y}} \\quad Z_2 = {round(z_max, 3)}"
            },
            {
                "paso_num": 2, "titulo": "Despejar la fórmula (X₁ y X₂)",
                "explicacion": "Usamos la fórmula del Puntaje Z despejada (Multiplicamos por la desviación y sumamos la media).",
                "formula_latex": f"X_1 = {media} + ({round(z_min, 3)} \\cdot {desviacion}) = {round(x_min, 2)}"
            },
            {
                "paso_num": 3, "titulo": "Calcular el segundo límite",
                "explicacion": "Repetimos el cálculo para el límite superior.",
                "formula_latex": f"X_2 = {media} + ({round(z_max, 3)} \\cdot {desviacion}) = {round(x_max, 2)}"
            }
        ]
    else:
        # Lógica para un solo valor
        if tipo_area == "menor":
            z = stats.norm.ppf(p1)
            area_prob = p1
        elif tipo_area == "mayor":
            z = stats.norm.ppf(1 - p1)  # Si queremos que el 5% sea mayor, buscamos el Z del 95%
            area_prob = p1
        elif tipo_area == "dos_colas":
            # Si dicen "Área 5% a dos colas", significa 2.5% en cada extremo
            cola = p1 / 2
            z = abs(stats.norm.ppf(1 - cola))  # Tomamos el Z positivo
            z2 = -z
            area_prob = p1
        elif tipo_area == "entre_media":
            # Si quieren 40% entre la media y Z, buscamos el Z que acumula 50% + 40%
            z = stats.norm.ppf(0.5 + p1)
            area_prob = p1

        x_val = media + (z * desviacion)

        pasos_didacticos = [
            {
                "paso_num": 1, "titulo": "Uso de la Función Inversa",
                "explicacion": f"Buscamos en la tabla Normal el Puntaje Z exacto que corresponde a un área o probabilidad de {round(p1, 4)}.",
                "formula_latex": f"Z = {round(z, 3)}"
            },
            {
                "paso_num": 2, "titulo": "Despejar X",
                "explicacion": "Tomamos la fórmula Z = (X - μ) / σ y despejamos la X: X = μ + (Z · σ)",
                "formula_latex": f"X = {media} + ({round(z, 3)} \\cdot {desviacion}) = {round(x_val, 2)}"
            }
        ]

        if tipo_area == "dos_colas":
            x2 = media + (z2 * desviacion)
            pasos_didacticos.append({
                "paso_num": 3, "titulo": "Simetría (Dos Colas)",
                "explicacion": "Como la campana es simétrica, tenemos un límite superior y uno inferior.",
                "formula_latex": f"X_{{inf}} = {round(x2, 2)} \\quad \\text{{y}} \\quad X_{{sup}} = {round(x_val, 2)}"
            })
            # Para el gráfico, en dos colas invertimos para que X1 sea el menor y X2 el mayor
            x_val, x2 = x2, x_val
            z, z2 = z2, z

    # 3. Reciclamos la lógica de renderizado del gráfico de la otra función
    # (Generamos los 100 puntos y las áreas pintadas)
    z_rango = np.linspace(-4, 4, 100)
    x_rango = z_rango * desviacion + media
    y_rango = stats.norm.pdf(z_rango, 0, 1)

    puntos_curva = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(x_rango, y_rango)]
    puntos_sombreados_1 = list()
    puntos_sombreados_2 = list()

    # Reconstruimos las sombras visuales basándonos en las X obtenidas
    if tipo_area == "menor":
        puntos_sombreados_1 = [p for p in puntos_curva if p['x'] <= x_val]
    elif tipo_area == "mayor":
        puntos_sombreados_1 = [p for p in puntos_curva if p['x'] >= x_val]
    elif tipo_area == "entre_media":
        puntos_sombreados_1 = [p for p in puntos_curva if min(media, x_val) <= p['x'] <= max(media, x_val)]
    elif tipo_area == "dos_colas":
        puntos_sombreados_1 = [p for p in puntos_curva if p['x'] <= x_val]
        puntos_sombreados_2 = [p for p in puntos_curva if p['x'] >= x2]
    elif tipo_area == "entre_dos_valores":
        puntos_sombreados_1 = [p for p in puntos_curva if min(x_val, x2) <= p['x'] <= max(x_val, x2)]

    return {
        "tema": "Proceso Inverso: Encontrar Puntaje (X)",
        "contexto": contexto,
        "simbolo_estadistico": "X",
        "datos_curva": puntos_curva,
        "sombreado_1": puntos_sombreados_1,
        "sombreado_2": puntos_sombreados_2,
        "paciente_x": round(x_val, 2),
        "paciente_z": round(z, 2),
        "paciente_x2": round(x2, 2) if x2 is not None else None,
        "paciente_z2": round(z2, 2) if z2 is not None else None,
        "percentil": round(area_prob * 100, 2),
        "tipo_area": tipo_area,
        "pasos": pasos_didacticos,
        "resultado_final": round(x_val, 2),
        "interpretacion": f"Para un área del {round(area_prob * 100, 2)}%, los valores de la variable original son {round(x_val, 2)}" + (
            f" y {round(x2, 2)}." if x2 is not None else ".")
    }