import collections


# ==========================================
# MÓDULO: LA MODA (El valor más frecuente)
# ==========================================

def calcular_moda_paso_a_paso(datos: list[float], contexto: str = "Puntajes") -> dict:
    if not datos: raise ValueError("No hay datos.")

    conteo = collections.Counter(datos)
    max_frecuencia = max(conteo.values())
    modas = [k for k, v in conteo.items() if v == max_frecuencia]

    # Lógica didáctica para explicar si hay 1, 2 o ninguna moda
    if max_frecuencia == 1:
        explicacion = "Todos los puntajes aparecen solo una vez. En este caso, decimos que la distribución es **Amodal** (no hay moda)."
        resultado = "Amodal"
    elif len(modas) == 1:
        explicacion = f"El puntaje que más se repite es {modas[0]}, apareciendo {max_frecuencia} veces. Es una distribución **Unimodal**."
        resultado = modas[0]
    else:
        explicacion = f"Hay un empate. Los puntajes {modas} se repiten {max_frecuencia} veces cada uno. Es una distribución **Multimodal**."
        resultado = modas

    return {
        "tema": "La Moda (Datos sin agrupar)",
        "contexto": contexto,
        "simbolo_estadistico": "Mo",
        "datos_originales": datos,
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Contar las repeticiones (Frecuencias)",
                "explicacion": "La Moda es simplemente el valor que está 'de moda', es decir, el que más se repite. Contamos cuántas veces aparece cada número.",
                "formula_latex": f"\\text{{Frecuencia Máxima detectada: }} {max_frecuencia}"
            },
            {
                "paso_num": 2,
                "titulo": "Identificar a los ganadores",
                "explicacion": explicacion,
                "formula_latex": f"Mo = {resultado}"
            }
        ],
        "resultado_final": str(resultado),
        "interpretacion": f"El valor más común o típico entre los pacientes es {resultado}."
    }


def calcular_moda_datos_agrupados(clases: list[dict], contexto: str = "Puntajes") -> dict:
    if not clases: raise ValueError("No hay datos.")

    # 1. Buscar la clase modal (la de mayor f)
    indice_modal = max(range(len(clases)), key=lambda i: clases[i]['f'])
    clase_modal = clases[indice_modal]
    f_i = clase_modal['f']

    # 2. Identificar frecuencias vecinas
    f_anterior = clases[indice_modal - 1]['f'] if indice_modal > 0 else 0
    f_siguiente = clases[indice_modal + 1]['f'] if indice_modal < len(clases) - 1 else 0

    # 3. Calcular deltas (d1 y d2)
    d1 = f_i - f_anterior
    d2 = f_i - f_siguiente

    # 4. Límites reales
    salto = 0
    if len(clases) > 1 and clases[1]['inf'] > clases[0]['sup']:
        salto = clases[1]['inf'] - clases[0]['sup']
    correccion = salto / 2
    L_real = clase_modal['inf'] - correccion
    S_real = clase_modal['sup'] + correccion
    Amplitud = S_real - L_real

    # 5. Calcular Moda
    moda = L_real + (d1 / (d1 + d2)) * Amplitud

    return {
        "tema": "La Moda (Datos Agrupados)",
        "contexto": contexto,
        "simbolo_estadistico": "Mo",
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Encontrar la 'Clase Modal'",
                "explicacion": f"Buscamos el grupo con mayor cantidad de pacientes (mayor f). Es el intervalo {clase_modal['inf']} - {clase_modal['sup']} con {f_i} pacientes.",
                "formula_latex": f"f_i = {f_i}"
            },
            {
                "paso_num": 2,
                "titulo": "Calcular las distancias con los vecinos (d₁ y d₂)",
                "explicacion": "Comparamos nuestro grupo ganador con el grupo anterior y el grupo siguiente para ver hacia dónde se inclina más la moda.",
                "formula_latex": f"d_1 = {f_i} - {f_anterior} = {d1} \\quad \\text{{y}} \\quad d_2 = {f_i} - {f_siguiente} = {d2}"
            },
            {
                "paso_num": 3,
                "titulo": "La Fórmula de Interpolación",
                "explicacion": f"Usamos el Límite Real Inferior (Lᵢ = {L_real}) y la Amplitud (A = {Amplitud}) en la fórmula de la moda.",
                "formula_latex": f"Mo = {L_real} + \\left( \\frac{{{d1}}}{{{d1} + {d2}}} \\right) \\cdot {Amplitud} = {round(moda, 2)}"
            }
        ],
        "resultado_final": round(moda, 2),
        "interpretacion": f"El valor más frecuente estimado en la muestra es {round(moda, 2)}."
    }
