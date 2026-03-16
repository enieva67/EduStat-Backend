# ==========================================
# MÓDULO: LA VARIANZA (Dispersión)
# ==========================================

def calcular_varianza_paso_a_paso(datos: list[float], contexto: str = "Puntajes") -> dict:
    n = len(datos)
    if n < 2: raise ValueError("Se necesitan al menos 2 datos para calcular la varianza.")

    media = sum(datos) / n
    suma_cuadrados = sum((x - media) ** 2 for x in datos)
    varianza = suma_cuadrados / (n - 1)  # Varianza Muestral

    # Didáctica visual: Mostrar solo las 3 primeras restas
    str_restas = " + ".join([f"({x} - {round(media, 1)})^2" for x in datos[:3]])
    if n > 3: str_restas += " + \\dots"

    return {
        "tema": "Varianza Muestral (Datos sin agrupar)",
        "contexto": contexto,
        "simbolo_estadistico": "S^2",
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Encontrar el centro (La Media)",
                "explicacion": "Para saber qué tan dispersos están los datos, primero necesitamos saber dónde está su centro.",
                "formula_latex": f"\\bar{{x}} = {round(media, 2)}"
            },
            {
                "paso_num": 2,
                "titulo": "Restar la media y elevar al cuadrado",
                "explicacion": "Calculamos qué tan lejos está CADA paciente del centro. Lo elevamos al cuadrado para que los números negativos se vuelvan positivos.",
                "formula_latex": f"\\Sigma (x_i - \\bar{{x}})^2 = {str_restas} = {round(suma_cuadrados, 2)}"
            },
            {
                "paso_num": 3,
                "titulo": "Dividir entre (n - 1)",
                "explicacion": f"Como es una muestra (no la población total), dividimos entre n-1 (grados de libertad) para no subestimar el error.",
                "formula_latex": f"S^2 = \\frac{{{round(suma_cuadrados, 2)}}}{{{n} - 1}} = {round(varianza, 2)}"
            }
        ],
        "resultado_final": round(varianza, 2),
        "interpretacion": f"Los '{contexto}' tienen una dispersión cuadrática promedio de {round(varianza, 2)}. (Para usar esta métrica en la vida real, se le suele sacar la raíz cuadrada)."
    }

def calcular_varianza_datos_agrupados(clases: list[dict], contexto: str = "Puntajes") -> dict:
    """Calcula la varianza muestral para datos agrupados con un enfoque ultra-didáctico."""
    if not clases: raise ValueError("No hay datos.")

    n_total = sum(c['f'] for c in clases)
    if n_total < 2: raise ValueError("Se necesitan al menos 2 datos (n>=2).")

    # 1. Necesitamos calcular la media primero
    suma_xf = 0
    detalles = []
    for c in clases:
        xi = (c['inf'] + c['sup']) / 2  # Marca de clase
        f = c['f']
        suma_xf += xi * f
        detalles.append({"intervalo": f"{c['inf']} - {c['sup']}", "xi": xi, "f": f})

    media = suma_xf / n_total

    # 2. Calcular Varianza (las distancias al cuadrado por su frecuencia)
    suma_cuadrados = 0
    for d in detalles:
        d['desviacion_cuad'] = (d['xi'] - media) ** 2
        d['f_desviacion_cuad'] = d['f'] * d['desviacion_cuad']
        suma_cuadrados += d['f_desviacion_cuad']

    varianza = suma_cuadrados / (n_total - 1)

    # Textos didácticos para no colapsar la pantalla con números
    c1 = detalles[0]
    explicacion_paso2 = f"Tomemos el grupo {c1['intervalo']} como ejemplo: su marca de clase es {c1['xi']}. Le restamos la media ({round(media, 2)}), lo elevamos al cuadrado para quitar negativos, y multiplicamos por los {c1['f']} pacientes que están en ese grupo."
    formula_paso2 = f"{c1['f']} \\cdot ({c1['xi']} - {round(media, 2)})^2 = {round(c1['f_desviacion_cuad'], 2)}"

    str_suma = " + ".join([f"{d['f']} \\cdot ({d['xi']} - {round(media, 1)})^2" for d in detalles[:2]])
    if len(detalles) > 2: str_suma += " + \\dots"

    return {
        "tema": "Varianza Muestral (Datos Agrupados)",
        "contexto": contexto,
        "simbolo_estadistico": "S^2",
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Calcular la Media (El Centro)",
                "explicacion": "Antes de medir la dispersión, necesitamos saber dónde está el centro del histograma. Usamos las Marcas de Clase (xᵢ) multiplicadas por sus frecuencias (f).",
                "formula_latex": f"\\bar{{x}} = \\frac{{\\Sigma x_i f}}{{n}} = \\frac{{{suma_xf}}}{{{n_total}}} = {round(media, 2)}"
            },
            {
                "paso_num": 2,
                "titulo": "Distancia al Centro (Para cada grupo)",
                "explicacion": explicacion_paso2,
                "formula_latex": formula_paso2
            },
            {
                "paso_num": 3,
                "titulo": "Sumar todas las dispersiones (Σf(xᵢ - x̄)²)",
                "explicacion": "Repetimos este cálculo engorroso para todos los grupos y sumamos los resultados para tener la Gran Suma Cuadrática.",
                "formula_latex": f"\\Sigma f(x_i - \\bar{{x}})^2 = {str_suma} = {round(suma_cuadrados, 2)}"
            },
            {
                "paso_num": 4,
                "titulo": "Dividir entre (n - 1)",
                "explicacion": "Finalmente, dividimos la gran suma entre el total de pacientes menos 1 (los grados de libertad de la muestra).",
                "formula_latex": f"S^2 = \\frac{{{round(suma_cuadrados, 2)}}}{{{n_total} - 1}} = {round(varianza, 2)}"
            }
        ],
        "resultado_final": round(varianza, 2),
        "interpretacion": f"La dispersión cuadrática estimada de los '{contexto}' es {round(varianza, 2)}. (Recordatorio: Sacando la raíz cuadrada a este valor obtenemos la famosa Desviación Estándar)."
    }