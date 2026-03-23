import math
import numpy as np
import scipy.stats as stats


def interpretar_correlacion(valor: float) -> str:
    abs_v = abs(valor)
    direccion = "positiva (si X sube, Y sube)" if valor > 0 else "negativa (si X sube, Y baja)"
    if abs_v < 0.2:
        fuerza = "muy débil o nula"
    elif abs_v < 0.4:
        fuerza = "débil"
    elif abs_v < 0.6:
        fuerza = "moderada"
    elif abs_v < 0.8:
        fuerza = "fuerte"
    else:
        fuerza = "muy fuerte"
    return f"Relación {direccion} y {fuerza}."


def calcular_pearson_paso_a_paso(x: list[float], y: list[float], ctx_x: str = "X", ctx_y: str = "Y") -> dict:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Las variables X e Y deben tener la misma cantidad de datos (mínimo 2).")

    n = len(x)
    mean_x, mean_y = sum(x) / n, sum(y) / n

    # Covarianza (Numerador) y Sumas de Cuadrados (Denominador)
    suma_productos = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    suma_cuad_x = sum((xi - mean_x) ** 2 for xi in x)
    suma_cuad_y = sum((yi - mean_y) ** 2 for yi in y)

    r = suma_productos / math.sqrt(suma_cuad_x * suma_cuad_y) if (suma_cuad_x * suma_cuad_y) != 0 else 0

    return {
        "tema": "Correlación de Pearson (Paramétrica)",
        "contexto": f"{ctx_x} vs {ctx_y}",
        "simbolo_estadistico": "r",
        "datos_x": x,
        "datos_y": y,
        "pasos": [
            {
                "paso_num": 1, "titulo": "Calcular las Medias",
                "explicacion": "Primero encontramos el centro de ambas variables.",
                "formula_latex": f"\\bar{{x}} = {round(mean_x, 2)} \\quad \\text{{y}} \\quad \\bar{{y}} = {round(mean_y, 2)}"
            },
            {
                "paso_num": 2, "titulo": "Covariación (¿Se mueven juntas?)",
                "explicacion": "Vemos qué tanto varían juntas. Restamos a cada dato su media y multiplicamos las diferencias de X con las de Y.",
                "formula_latex": f"\\Sigma (x - \\bar{{x}})(y - \\bar{{y}}) = {round(suma_productos, 2)}"
            },
            {
                "paso_num": 3, "titulo": "Variabilidad Individual",
                "explicacion": "Calculamos cuánto varía cada variable por su cuenta (Suma de cuadrados).",
                "formula_latex": f"\\Sigma (x - \\bar{{x}})^2 = {round(suma_cuad_x, 2)} \\quad \\text{{y}} \\quad \\Sigma (y - \\bar{{y}})^2 = {round(suma_cuad_y, 2)}"
            },
            {
                "paso_num": 4, "titulo": "El Coeficiente (r)",
                "explicacion": "Dividimos la variación conjunta entre la variación individual estandarizada.",
                "formula_latex": f"r = \\frac{{{round(suma_productos, 2)}}}{{\\sqrt{{{round(suma_cuad_x, 2)} \\cdot {round(suma_cuad_y, 2)}}}}} = {round(r, 3)}"
            }
        ],
        "resultado_final": round(r, 3),
        "interpretacion": interpretar_correlacion(r)
    }


def calcular_spearman_paso_a_paso(x: list[float], y: list[float], ctx_x: str = "X", ctx_y: str = "Y") -> dict:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("X e Y deben tener la misma cantidad de datos.")

    n = len(x)
    # Convertimos los datos crudos a RANGOS (Posiciones 1º, 2º, 3º...)
    rangos_x = stats.rankdata(x)
    rangos_y = stats.rankdata(y)

    # Diferencias de rangos
    diferencias = rangos_x - rangos_y
    d2 = diferencias ** 2
    suma_d2 = sum(d2)

    # Cálculo con scipy para manejar empates (ties) a la perfección
    rho, _ = stats.spearmanr(x, y)

    # Textos didácticos
    ejemplo_x = f"El dato {x[0]} de X quedó en la posición {rangos_x[0]}º."

    return {
        "tema": "Correlación de Spearman (No Paramétrica)",
        "contexto": f"{ctx_x} vs {ctx_y}",
        "simbolo_estadistico": "\\rho",  # Letra griega Rho
        "datos_x": x,
        "datos_y": y,
        "pasos": [
            {
                "paso_num": 1, "titulo": "Convertir a Rangos",
                "explicacion": f"Spearman no usa los números reales, sino sus posiciones en un ranking (de menor a mayor). {ejemplo_x}",
                "formula_latex": "\\text{Se asignan rangos } R_x \\text{ y } R_y"
            },
            {
                "paso_num": 2, "titulo": "Diferencia de Rangos (d)",
                "explicacion": "A cada paciente le restamos el rango que obtuvo en Y menos el rango que obtuvo en X, y lo elevamos al cuadrado (d²).",
                "formula_latex": f"\\Sigma d^2 = {round(suma_d2, 2)}"
            },
            {
                "paso_num": 3, "titulo": "Fórmula de Spearman",
                "explicacion": "Aplicamos la fórmula clásica basada en las diferencias de posición.",
                "formula_latex": f"\\rho = 1 - \\frac{{6 \\cdot {round(suma_d2, 2)}}}{{{n}({n}^2 - 1)}} \\approx {round(rho, 3)}"
            }
        ],
        "resultado_final": round(rho, 3),
        "interpretacion": interpretar_correlacion(rho)
    }


def calcular_phi_paso_a_paso(x: list[float], y: list[float], ctx_x: str = "X", ctx_y: str = "Y") -> dict:
    # Validamos que solo haya ceros y unos (Python entiende perfectamente que 1.0 es 1)
    if not set(x).issubset({0, 1}) or not set(y).issubset({0, 1}):
        raise ValueError("El Coeficiente Phi requiere que ambas variables sean Dicotómicas (solo ceros y unos).")

    if len(x) != len(y) or len(x) < 2:
        raise ValueError("X e Y deben tener la misma cantidad de datos.")

    # Construir tabla de contingencia 2x2
    # a: X=1, Y=1 | b: X=1, Y=0 | c: X=0, Y=1 | d: X=0, Y=0
    a = sum(1 for xi, yi in zip(x, y) if xi == 1 and yi == 1)
    b = sum(1 for xi, yi in zip(x, y) if xi == 1 and yi == 0)
    c = sum(1 for xi, yi in zip(x, y) if xi == 0 and yi == 1)
    d = sum(1 for xi, yi in zip(x, y) if xi == 0 and yi == 0)

    numerador = (a * d) - (b * c)
    denominador = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    phi = numerador / denominador if denominador != 0 else 0

    return {
        "tema": "Coeficiente Phi (Variables Dicotómicas)",
        "contexto": f"{ctx_x} vs {ctx_y}",
        "simbolo_estadistico": "\\phi",
        "datos_x": x,
        "datos_y": y,
        "pasos": [
            {
                "paso_num": 1, "titulo": "Tabla de Contingencia 2x2",
                "explicacion": "Contamos los casos en una matriz. Arriba a la izquierda (a) están los que sacaron 1 en ambas. Abajo a la derecha (d) los que sacaron 0 en ambas.",
                # LA MAGIA CORREGIDA: Usamos un entorno de Matriz LaTeX real
                "formula_latex": f"\\begin{{bmatrix}} a={a} & b={b} \\\\ c={c} & d={d} \\end{{bmatrix}}"
            },
            {
                "paso_num": 2, "titulo": "Multiplicación Cruzada",
                "explicacion": "Multiplicamos las diagonales de la tabla y las restamos (ad - bc).",
                "formula_latex": f"({a} \\cdot {d}) - ({b} \\cdot {c}) = {numerador}"
            },
            {
                "paso_num": 3, "titulo": "Fórmula de Phi (φ)",
                "explicacion": "Dividimos por la raíz de los productos de todos los totales marginales.",
                "formula_latex": f"\\phi = \\frac{{{numerador}}}{{\\sqrt{{({a}+{b})({c}+{d})({a}+{c})({b}+{d})}}}} = {round(phi, 3)}"
            }
        ],
        "resultado_final": round(phi, 3),
        "interpretacion": interpretar_correlacion(phi)
    }
