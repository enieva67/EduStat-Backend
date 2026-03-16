# Archivo: app/services/estadistica/tendencia_central.py

def calcular_media_paso_a_paso(datos: list[float], contexto: str = "Puntajes") -> dict:
    """Calcula la media aritmética evaluando si debe usar el Modo Estudiante o Modo Analista."""
    if not datos:
        raise ValueError("La lista de datos no puede estar vacía.")

    n = len(datos)
    suma_total = sum(datos)
    media = suma_total / n

    # ==========================================
    # MODO ANALISTA (N > 300): Desactivar desglose
    # ==========================================
    if n > 300:
        return {
            "tema": "Media Aritmética (Modo Analista)",
            "contexto": contexto,
            "simbolo_estadistico": "\\bar{x}",
            "pasos":[
                {
                    "paso_num": 1,
                    "titulo": "Análisis de Gran Volumen",
                    "explicacion": f"Has ingresado {n} datos. Para optimizar el rendimiento y enfocarnos en el análisis, el modo 'Paso a Paso' se ha desactivado. Hemos procesado la sumatoria internamente.",
                    "formula_latex": f"n = {n} \\quad \\Sigma x = {round(suma_total, 2)}",
                },
                {
                    "paso_num": 2,
                    "titulo": "Resultado Directo",
                    "explicacion": "Aplicando la fórmula clásica de la media muestral:",
                    "formula_latex": f"\\bar{{x}} = \\frac{{\\Sigma x}}{{n}} = {round(media, 4)}"
                }
            ],
            "resultado_final": round(media, 4),
            "interpretacion": f"El promedio de los {n} registros de '{contexto}' es de {round(media, 4)}."
        }

    # ==========================================
    # MODO ESTUDIANTE (N <= 300): Clase Magistral
    # ==========================================
    datos_str = " + ".join(map(str, datos[:5]))
    if n > 5:
        datos_str += " + \\dots + " + str(datos[-1])

    return {
        "tema": "Media Aritmética (Datos sin agrupar)",
        "contexto": contexto,
        "simbolo_estadistico": "\\bar{x}",
        "datos_originales": datos,  # <--- ¡AÑADE ESTA LÍNEA AQUÍ!
        "pasos":[
            {
                "paso_num": 1,
                "titulo": "Reunir los datos (Σx)",
                "explicacion": "El primer paso es sumar todos los valores observados.",
                "formula_latex": f"\\Sigma x = {datos_str} = {round(suma_total, 2)}",
            },
            {
                "paso_num": 2,
                "titulo": "Contar los casos (n)",
                "explicacion": "¿A cuántos individuos o casos evaluamos en total?",
                "formula_latex": f"n = {n}",
            },
            {
                "paso_num": 3,
                "titulo": "Dividir equitativamente",
                "explicacion": "Repartimos el gran total entre el número de casos para encontrar el punto de equilibrio o 'promedio'.",
                "formula_latex": f"\\bar{{x}} = \\frac{{\\Sigma x}}{{n}} = \\frac{{{round(suma_total, 2)}}}{{{n}}} = {round(media, 2)}",
            }
        ],
        "resultado_final": round(media, 2),
        "interpretacion": f"En promedio, el valor de los '{contexto}' es de {round(media, 2)}."
    }


def calcular_media_datos_agrupados(clases: list[dict], contexto: str = "Puntajes") -> dict:
    """
    Calcula la media para datos AGRUPADOS en intervalos.
    Espera una lista de diccionarios con 'inf' (límite inferior), 'sup' (límite superior) y 'f' (frecuencia).
    Ejemplo:[{"inf": 10, "sup": 19, "f": 5}, {"inf": 20, "sup": 29, "f": 12}]
    """
    if not clases:
        raise ValueError("No hay datos para procesar.")

    n_total = 0
    suma_productos = 0
    detalles_clases = []

    # Procesamos la tabla y hacemos los cálculos matemáticos
    for c in clases:
        lim_inf = c['inf']
        lim_sup = c['sup']
        frecuencia = c['f']

        # 1. Calcular Marca de Clase (Punto Medio)
        marca_clase = (lim_inf + lim_sup) / 2

        # 2. Multiplicar Marca por Frecuencia
        producto = marca_clase * frecuencia

        n_total += frecuencia
        suma_productos += producto

        detalles_clases.append({
            "intervalo": f"{lim_inf} - {lim_sup}",
            "xi": marca_clase,
            "f": frecuencia,
            "xi_f": producto
        })

    media = suma_productos / n_total

    # Para no saturar la pantalla con fórmulas gigantes, tomamos la primera clase como ejemplo didáctico
    ejemplo = detalles_clases[0]

    # Construimos el texto de la sumatoria total (solo los primeros 3 para no desbordar la pantalla)
    suma_str_lista = [f"({c['xi']} \\cdot {c['f']})" for c in detalles_clases[:3]]
    suma_str = " + ".join(suma_str_lista)
    if len(detalles_clases) > 3:
        suma_str += " + \\dots"

    datos_histograma = []
    for c in detalles_clases:
        datos_histograma.append({
            "intervalo": c['intervalo'],
            "xi": c['xi'],  # Marca de clase (Eje X)
            "f": c['f']  # Frecuencia (Altura de la barra, Eje Y)
        })
    # El Contrato JSON Didáctico
        respuesta_didactica = {
            "tema": "Media Aritmética (Datos Agrupados)",
            "contexto": contexto,
            "simbolo_estadistico": "\\bar{x}",
            "datos_histograma": datos_histograma,  # <--- ¡AÑADIMOS ESTO AQUÍ!
            "pasos": [
                {
                "paso_num": 1,
                "titulo": "Hallar el Representante (Marca de Clase xᵢ)",  # <-- Unicode aquí
                "explicacion": f"Como no sabemos el puntaje exacto de cada persona, buscamos el punto medio de cada intervalo. Por ejemplo, para el primer grupo ({ejemplo['intervalo']}):",
                "formula_latex": f"x_1 = \\frac{{{ejemplo['intervalo'].replace(' - ', ' + ')}}}{{2}} = {ejemplo['xi']}",
            },
            {
                "paso_num": 2,
                "titulo": "Multiplicar por la cantidad de casos (xᵢ · f)",  # <-- Unicode aquí
                "explicacion": f"Asumimos que las {ejemplo['f']} personas del primer grupo sacaron {ejemplo['xi']}. Así que multiplicamos:",
                "formula_latex": f"{ejemplo['xi']} \\cdot {ejemplo['f']} = {ejemplo['xi_f']}",
            },
            {
                "paso_num": 3,
                "titulo": "Sumar todos los grupos (Σxᵢf)",  # <-- Unicode aquí
                "explicacion": "Repetimos este proceso para todos los grupos y sumamos los resultados para obtener el 'Gran Total' estimado.",
                "formula_latex": f"\\Sigma x_i f = {suma_str} = {suma_productos}",
            },
            {
                "paso_num": 4,
                "titulo": "Dividir entre el total de casos (n)",
                "explicacion": f"Finalmente, dividimos ese gran total ({suma_productos}) entre el total de pacientes evaluados (n = {n_total}).",
                "formula_latex": f"\\bar{{x}} = \\frac{{\\Sigma x_i f}}{{n}} = \\frac{{{suma_productos}}}{{{n_total}}} = {round(media, 2)}",
            }
        ],
        "resultado_final": round(media, 2),
        "interpretacion": f"Si consideramos los datos agrupados, el promedio estimado de los '{contexto}' es de {round(media, 2)}."
    }

    return respuesta_didactica


# --- NUEVAS FUNCIONES PARA LA MEDIANA ---

def calcular_mediana_paso_a_paso(datos: list[float], contexto: str = "Puntajes") -> dict:
    """Calcula la mediana para datos SIN agrupar."""
    if not datos:
        raise ValueError("La lista de datos no puede estar vacía.")

    n = len(datos)
    datos_ordenados = sorted(datos)

    # Textos para la explicación
    datos_str = ", ".join(map(str, datos_ordenados[:10]))
    if n > 10:
        datos_str += ", \\dots"

    pasos = [
        {
            "paso_num": 1,
            "titulo": "Ordenar los datos",
            "explicacion": "La Mediana es el valor que está exactamente en el medio. Pero para encontrarlo, primero DEBEMOS ordenar a los pacientes de menor a mayor puntaje.",
            "formula_latex": f"\\text{{Ordenados: }} [{datos_str}]"
        }
    ]

    if n % 2 != 0:
        # Impar
        pos = (n + 1) // 2
        mediana = datos_ordenados[pos - 1]
        pasos.extend([
            {
                "paso_num": 2,
                "titulo": "Encontrar la Posición Central (n es Impar)",
                "explicacion": f"Como tenemos {n} pacientes (un número impar), hay un único paciente en el centro exacto. Su posición es (n+1)/2.",
                "formula_latex": f"Pos = \\frac{{{n} + 1}}{{2}} = {pos}"
            },
            {
                "paso_num": 3,
                "titulo": "Identificar la Mediana",
                "explicacion": f"Buscamos al paciente en la posición {pos} de nuestra lista ordenada.",
                "formula_latex": f"Me = {mediana}"
            }
        ])
    else:
        # Par
        pos1 = n // 2
        pos2 = pos1 + 1
        val1 = datos_ordenados[pos1 - 1]
        val2 = datos_ordenados[pos2 - 1]
        mediana = (val1 + val2) / 2
        pasos.extend([
            {
                "paso_num": 2,
                "titulo": "Encontrar el Centro (n es Par)",
                "explicacion": f"Como tenemos {n} pacientes (un número par), la lista se parte en dos y quedan DOS pacientes en el centro (posiciones n/2 y n/2 + 1).",
                "formula_latex": f"Pos_1 = {pos1}, \\quad Pos_2 = {pos2}"
            },
            {
                "paso_num": 3,
                "titulo": "Promediar los dos centros",
                "explicacion": f"Los pacientes en el centro tienen los puntajes {val1} y {val2}. La mediana es el promedio de ambos.",
                "formula_latex": f"Me = \\frac{{{val1} + {val2}}}{{2}} = {mediana}"
            }
        ])

    return {
        "tema": "Mediana (Datos sin agrupar)",
        "contexto": contexto,
        "simbolo_estadistico": "Me",
        "datos_originales": datos_ordenados,  # Para dibujar el Dot Plot ordenado
        "pasos": pasos,
        "resultado_final": round(mediana, 2),
        "interpretacion": f"El 50% de los '{contexto}' están por debajo de {round(mediana, 2)}, y el otro 50% por encima."
    }


def calcular_mediana_datos_agrupados(clases: list[dict], contexto: str = "Puntajes") -> dict:
    """Calcula la mediana magistral para datos AGRUPADOS en intervalos."""
    if not clases:
        raise ValueError("No hay datos para procesar.")

    n_total = 0
    F_acumulada = 0
    tabla_F = []

    # 1. Calcular Frecuencias Acumuladas
    for c in clases:
        F_acumulada += c['f']
        n_total += c['f']
        tabla_F.append({
            "inf": c['inf'], "sup": c['sup'], "f": c['f'], "F": F_acumulada
        })

    # 2. Posición de la Mediana
    posicion = n_total / 2

    # 3. Encontrar Clase Mediana
    clase_mediana = None
    F_anterior = 0
    for i, fila in enumerate(tabla_F):
        if fila['F'] >= posicion:
            clase_mediana = fila
            if i > 0:
                F_anterior = tabla_F[i - 1]['F']
            break

    if not clase_mediana:
        raise ValueError("Error al calcular la clase mediana.")

    # 4. Magia Didáctica: Calcular Límite Real y Amplitud
    L_aparente = clase_mediana['inf']
    S_aparente = clase_mediana['sup']
    f_i = clase_mediana['f']

    # Verificamos si hay "saltos" entre clases para aplicar la regla de Límite Exacto (-0.5)
    salto = 0
    if len(clases) > 1 and clases[1]['inf'] > clases[0]['sup']:
        salto = clases[1]['inf'] - clases[0]['sup']

    correccion = salto / 2
    L_real = L_aparente - correccion
    S_real = S_aparente + correccion
    Amplitud = S_real - L_real

    # 5. La Fórmula Maestra
    fraccion = (posicion - F_anterior) / f_i
    mediana = L_real + (fraccion * Amplitud)

    # Texto didáctico para los límites
    explicacion_limites = f"El intervalo ganador es {L_aparente} - {S_aparente}. "
    if correccion > 0:
        explicacion_limites += f"Como tus intervalos tienen saltos (ej. 84 a 85), calculamos el 'Límite Real Inferior' (Lᵢ) restando {correccion}: Lᵢ = {L_real}. Y la amplitud exacta (A) es {Amplitud}."
    else:
        explicacion_limites += f"El Límite Inferior (Lᵢ) es {L_real} y la Amplitud (A) es {Amplitud}."

    return {
        "tema": "Mediana (Datos Agrupados)",
        "contexto": contexto,
        "simbolo_estadistico": "Me",
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Frecuencia Acumulada (F)",
                "explicacion": "Para encontrar al paciente del medio, primero debemos enfilarlos. Creamos una columna sumando los pacientes grupo por grupo (F).",
                "formula_latex": "\\text{Se calcula la Frecuencia Acumulada. Total: } n = " + str(n_total)
            },
            {
                "paso_num": 2,
                "titulo": "Posición Central (n/2)",
                "explicacion": "Dividimos el total de pacientes entre 2 para saber en qué 'silla' está sentada la Mediana.",
                "formula_latex": f"Pos = \\frac{{{n_total}}}{{2}} = {posicion}"
            },
            {
                "paso_num": 3,
                "titulo": "Buscar la Clase Mediana",
                "explicacion": f"Buscamos en la Frecuencia Acumulada (F) el primer grupo que contenga o supere la posición {posicion}.",
                "formula_latex": f"\\text{{Clase Mediana: }} {L_aparente} - {S_aparente} \\quad (f_i = {f_i}, F_{{i-1}} = {F_anterior})"
            },
            {
                "paso_num": 4,
                "titulo": "Extraer los Datos Exactos",
                "explicacion": explicacion_limites,
                "formula_latex": f"L_i = {L_real}, \\quad A = {Amplitud}, \\quad F_{{i-1}} = {F_anterior}, \\quad f_i = {f_i}"
            },
            {
                "paso_num": 5,
                "titulo": "La Fórmula de Interpolación",
                "explicacion": "Finalmente, armamos la ecuación para estimar en qué punto exacto dentro de ese intervalo cayó nuestra Mediana.",
                "formula_latex": f"Me = {L_real} + \\left( \\frac{{{posicion} - {F_anterior}}}{{{f_i}}} \\right) \\cdot {Amplitud} = {round(mediana, 2)}"
            }
        ],
        "resultado_final": round(mediana, 2),
        "interpretacion": f"Estimamos que el 50% de los pacientes tienen un puntaje de '{contexto}' inferior a {round(mediana, 2)}."
    }


# ==========================================
# MÓDULO: MEDIDAS DE POSICIÓN (Percentiles)
# ==========================================

def _traducir_percentil(k: int) -> str:
    """Función auxiliar para darle contexto didáctico al percentil pedido."""
    if k == 25: return "Percentil 25 (También conocido como 1er Cuartil - Q1)"
    if k == 50: return "Percentil 50 (También conocido como Mediana - Q2)"
    if k == 75: return "Percentil 75 (También conocido como 3er Cuartil - Q3)"
    if k % 10 == 0: return f"Percentil {k} (También conocido como Decil {k // 10})"
    return f"Percentil {k}"


def calcular_percentil_paso_a_paso(datos: list[float], contexto: str = "Puntajes", k: int = 50) -> dict:
    if not datos: raise ValueError("No hay datos.")
    if not (1 <= k <= 99): raise ValueError("El percentil (k) debe estar entre 1 y 99.")

    n = len(datos)
    datos_ordenados = sorted(datos)

    # Fórmula clásica de posición: k(n+1)/100
    pos_exacta = (k * (n + 1)) / 100

    # Interpolación simple para no enredar al estudiante
    idx_inferior = int(pos_exacta) - 1

    if idx_inferior < 0:
        percentil = datos_ordenados[0]
    elif idx_inferior >= n - 1:
        percentil = datos_ordenados[-1]
    else:
        # Si la posición dio 3.25, buscamos el valor 3 y le sumamos el 0.25 de la distancia al valor 4
        decimal = pos_exacta - int(pos_exacta)
        val_inf = datos_ordenados[idx_inferior]
        val_sup = datos_ordenados[idx_inferior + 1]
        percentil = val_inf + decimal * (val_sup - val_inf)

    nombre_k = _traducir_percentil(k)

    return {
        "tema": f"Medida de Posición: {nombre_k}",
        "contexto": contexto,
        "simbolo_estadistico": f"P_{{{k}}}",
        "datos_originales": datos_ordenados,
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Ordenar los datos",
                "explicacion": "Al igual que con la Mediana, para buscar una posición, el paso CERO es ordenar a los pacientes de menor a mayor.",
                "formula_latex": f"\\text{{Ordenados: }}[{datos_ordenados[0]}, {datos_ordenados[1]}, \\dots, {datos_ordenados[-1]}]"
            },
            {
                "paso_num": 2,
                "titulo": f"Buscar la Posición del {k}%",
                "explicacion": f"Usamos la fórmula de posición para dividir los {n} pacientes en 100 partes y avanzar hasta la porción {k}.",
                "formula_latex": f"Pos = \\frac{{{k} \\cdot ({n} + 1)}}{{100}} = {round(pos_exacta, 2)}"
            },
            {
                "paso_num": 3,
                "titulo": "Encontrar el Valor Exacto (Interpolación)",
                "explicacion": f"Buscamos en nuestra lista ordenada la posición {round(pos_exacta, 2)}. Como cae entre dos personas, calculamos la distancia exacta entre ellos.",
                "formula_latex": f"P_{{{k}}} = {round(percentil, 2)}"
            }
        ],
        "resultado_final": round(percentil, 2),
        "interpretacion": f"El {k}% de los pacientes tiene un '{contexto}' igual o menor a {round(percentil, 2)}."
    }


def calcular_percentil_datos_agrupados(clases: list[dict], contexto: str = "Puntajes", k: int = 50) -> dict:
    if not clases: raise ValueError("No hay datos.")
    if not (1 <= k <= 99): raise ValueError("El percentil (k) debe estar entre 1 y 99.")

    n_total = sum(c['f'] for c in clases)
    F_acumulada = 0
    tabla_F = []

    for c in clases:
        F_acumulada += c['f']
        tabla_F.append({"inf": c['inf'], "sup": c['sup'], "f": c['f'], "F": F_acumulada})

    # Posición para percentiles: (k * n) / 100
    posicion = (k * n_total) / 100

    clase_p = None
    F_anterior = 0
    for i, fila in enumerate(tabla_F):
        if fila['F'] >= posicion:
            clase_p = fila
            if i > 0: F_anterior = tabla_F[i - 1]['F']
            break

    if not clase_p: raise ValueError("Error calculando la clase del percentil.")

    f_i = clase_p['f']
    salto = clases[1]['inf'] - clases[0]['sup'] if len(clases) > 1 and clases[1]['inf'] > clases[0]['sup'] else 0
    correccion = salto / 2
    L_real = clase_p['inf'] - correccion
    S_real = clase_p['sup'] + correccion
    Amplitud = S_real - L_real

    # Fórmula (IDÉNTICA a la Mediana)
    percentil = L_real + ((posicion - F_anterior) / f_i) * Amplitud
    nombre_k = _traducir_percentil(k)

    return {
        "tema": f"Medida de Posición: {nombre_k} (Agrupados)",
        "contexto": contexto,
        "simbolo_estadistico": f"P_{{{k}}}",
        "pasos": [
            {
                "paso_num": 1,
                "titulo": "Frecuencia Acumulada (F)",
                "explicacion": "Como siempre en medidas de posición, usamos la Frecuencia Acumulada para ir sumando pacientes.",
                "formula_latex": f"n = {n_total}"
            },
            {
                "paso_num": 2,
                "titulo": f"Buscar la Posición del {k}%",
                "explicacion": f"En lugar de dividir entre 2 (como en la Mediana), multiplicamos por {k} y dividimos entre 100.",
                "formula_latex": f"Pos = \\frac{{{k} \\cdot n}}{{100}} = \\frac{{{k} \\cdot {n_total}}}{{100}} = {round(posicion, 2)}"
            },
            {
                "paso_num": 3,
                "titulo": "Extraer los Datos del Grupo",
                "explicacion": f"Buscamos la posición {round(posicion, 2)} en la Frecuencia Acumulada. Cae en el intervalo {clase_p['inf']} - {clase_p['sup']}. Su límite inferior real es Lᵢ = {L_real}.",
                "formula_latex": f"L_i = {L_real}, \\quad A = {Amplitud}, \\quad F_{{i-1}} = {F_anterior}, \\quad f_i = {f_i}"
            },
            {
                "paso_num": 4,
                "titulo": "Fórmula de Interpolación (Igual a la Mediana)",
                "explicacion": "Aplicamos exactamente la misma fórmula que en la Mediana, pero usando nuestra nueva Posición.",
                "formula_latex": f"P_{{{k}}} = {L_real} + \\left( \\frac{{{round(posicion, 2)} - {F_anterior}}}{{{f_i}}} \\right) \\cdot {Amplitud} = {round(percentil, 2)}"
            }
        ],
        "resultado_final": round(percentil, 2),
        "interpretacion": f"El {k}% de los pacientes tiene un puntaje de '{contexto}' inferior o igual a {round(percentil, 2)}."
    }