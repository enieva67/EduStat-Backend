import math
import numpy as np
import scipy.stats as stats


def calcular_intervalo_confianza_media(media_muestral: float, desviacion: float, n: int, confianza: float = 95.0,
                                       contexto: str = "Variable") -> dict:
    if n < 2: raise ValueError("El tamaño de la muestra (n) debe ser al menos 2 para calcular el error.")
    if desviacion <= 0: raise ValueError("La desviación estándar debe ser mayor a cero.")
    if not (0 < confianza < 100): raise ValueError("El nivel de confianza debe estar entre 0 y 100 (Ej: 95).")

    # Alfa es el nivel de riesgo (lo que queda fuera del intervalo)
    alpha = 1 - (confianza / 100.0)

    # 1. Lógica Didáctica: ¿Z o T de Student?
    usa_z = n >= 30
    if usa_z:
        valor_critico = stats.norm.ppf(1 - alpha / 2)
        dist_nombre = "Normal Estándar (Z)"
        simbolo_crit = "Z_{\\alpha/2}"
    else:
        df = n - 1  # Grados de libertad
        valor_critico = stats.t.ppf(1 - alpha / 2, df)
        dist_nombre = f"T de Student (gl={df})"
        simbolo_crit = "t_{\\alpha/2}"

    # 2. Cálculos matemáticos
    error_estandar = desviacion / math.sqrt(n)
    margen_error = valor_critico * error_estandar

    lim_inf = media_muestral - margen_error
    lim_sup = media_muestral + margen_error

    # 3. Construimos los 100 puntos para que Flutter dibuje la campana de muestreo
    # El centro del gráfico ahora es la Media Muestral, y la dispersión es el Error Estándar
    rango_x = np.linspace(media_muestral - 4 * error_estandar, media_muestral + 4 * error_estandar, 100)

    if usa_z:
        rango_y = stats.norm.pdf(rango_x, media_muestral, error_estandar)
    else:
        rango_y = stats.t.pdf((rango_x - media_muestral) / error_estandar, df)

    puntos_curva = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(rango_x, rango_y)]

    # Pintamos el centro (El Intervalo)
    puntos_sombreados_1 = [p for p in puntos_curva if lim_inf <= p['x'] <= lim_sup]

    return {
        "tema": f"Intervalo de Confianza al {confianza}%",
        "contexto": contexto,
        "simbolo_estadistico": "IC",
        "datos_curva": puntos_curva,
        "sombreado_1": puntos_sombreados_1,
        "sombreado_2": [],  # Vacío
        "paciente_x": round(lim_inf, 2),  # Reciclamos esta variable para el Límite Inferior
        "paciente_x2": round(lim_sup, 2),  # Reciclamos esta variable para el Límite Superior
        "paciente_z": 0.0,  # Dummy
        "percentil": confianza,
        "tipo_area": "entre_dos_valores",  # Le dice a Flutter que dibuje las dos líneas
        "pasos": [
            {
                "paso_num": 1, "titulo": f"Selección de Distribución ({dist_nombre})",
                "explicacion": f"Como tenemos n={n} datos, la teoría nos dicta usar la distribución {dist_nombre}. Buscamos en la tabla el valor crítico que encierra el {confianza}% en el centro.",
                "formula_latex": f"{simbolo_crit} = {round(valor_critico, 3)}"
            },
            {
                "paso_num": 2, "titulo": "Error Estándar (SE)",
                "explicacion": "Calculamos qué tanto podría variar nuestra media muestral respecto a la verdadera media de la población.",
                "formula_latex": f"SE = \\frac{{{desviacion}}}{{\\sqrt{{{n}}}}} = {round(error_estandar, 3)}"
            },
            {
                "paso_num": 3, "titulo": "Margen de Error (ME)",
                "explicacion": "Multiplicamos nuestro valor crítico por el Error Estándar. Esto nos dice cuánto nos podemos equivocar hacia arriba o hacia abajo.",
                "formula_latex": f"ME = {round(valor_critico, 3)} \\cdot {round(error_estandar, 3)} = {round(margen_error, 2)}"
            },
            {
                "paso_num": 4, "titulo": "Construir el Intervalo",
                "explicacion": "A nuestra media muestral le sumamos y restamos el Margen de Error.",
                "formula_latex": f"IC = {media_muestral} \\pm {round(margen_error, 2)} =[{round(lim_inf, 2)}, {round(lim_sup, 2)}]"
            }
        ],
        "resultado_final": round(margen_error, 2),
        "interpretacion": f"Estamos {confianza}% seguros de que la verdadera media poblacional de '{contexto}' está entre {round(lim_inf, 2)} y {round(lim_sup, 2)}."
    }


def calcular_prueba_hipotesis_media(mu_pob: float, x_barra: float, desviacion: float, n: int, alfa: float = 0.05,
                                    tipo_prueba: str = "dos_colas", contexto: str = "Variable") -> dict:
    if n < 2: raise ValueError("El tamaño de la muestra (n) debe ser al menos 2.")
    if desviacion <= 0: raise ValueError("La desviación estándar debe ser mayor a cero.")
    if not (0 < alfa < 1): raise ValueError("Alfa debe estar entre 0 y 1 (Ej: 0.05).")

    # 1. Definir Hipótesis en LaTeX
    if tipo_prueba == "dos_colas":
        h1_latex = f"H_1: \\mu \\neq {mu_pob}"
        explicacion_h1 = "dos colas (queremos saber si es diferente, mayor o menor)."
    elif tipo_prueba == "cola_der":
        h1_latex = f"H_1: \\mu > {mu_pob}"
        explicacion_h1 = "cola derecha (queremos saber si es significativamente mayor)."
    else:  # cola_izq
        h1_latex = f"H_1: \\mu < {mu_pob}"
        explicacion_h1 = "cola izquierda (queremos saber si es significativamente menor)."

    # 2. ¿Z o T de Student?
    usa_z = n >= 30
    df = n - 1
    dist = stats.norm if usa_z else stats.t
    args_dist = () if usa_z else (df,)
    nombre_test = "Prueba Z" if usa_z else "Prueba T de Student"
    simbolo_stat = "Z" if usa_z else "t"

    # 3. Matemáticas
    error_estandar = desviacion / math.sqrt(n)
    stat_prueba = (x_barra - mu_pob) / error_estandar

    # 4. Valores Críticos y Valor P
    if tipo_prueba == "dos_colas":
        crit_inf = dist.ppf(alfa / 2, *args_dist)
        crit_sup = dist.ppf(1 - alfa / 2, *args_dist)
        p_valor = 2 * (1 - dist.cdf(abs(stat_prueba), *args_dist))
        str_critico = f"\\pm {round(crit_sup, 3)}"
        rechazo = stat_prueba <= crit_inf or stat_prueba >= crit_sup
    elif tipo_prueba == "cola_der":
        crit_sup = dist.ppf(1 - alfa, *args_dist)
        crit_inf = -float('inf')  # No hay rechazo por abajo
        p_valor = 1 - dist.cdf(stat_prueba, *args_dist)
        str_critico = f"{round(crit_sup, 3)}"
        rechazo = stat_prueba >= crit_sup
    else:  # cola_izq
        crit_inf = dist.ppf(alfa, *args_dist)
        crit_sup = float('inf')  # No hay rechazo por arriba
        p_valor = dist.cdf(stat_prueba, *args_dist)
        str_critico = f"{round(crit_inf, 3)}"
        rechazo = stat_prueba <= crit_inf

    # Conclusión en texto
    decision = "RECHAZAMOS" if rechazo else "NO RECHAZAMOS"
    conclusion_texto = f"Como el p-valor ({round(p_valor, 4)}) es {'menor' if rechazo else 'mayor'} que alfa ({alfa}), {decision} la Hipótesis Nula."

    # 5. Geometría de la Campana (Visualización)
    # Dibujamos centrando en la Hipótesis Nula (Mundo Teórico)
    rango_x = np.linspace(mu_pob - 4 * error_estandar, mu_pob + 4 * error_estandar, 100)
    if usa_z:
        rango_y = stats.norm.pdf(rango_x, mu_pob, error_estandar)
    else:
        rango_y = stats.t.pdf((rango_x - mu_pob) / error_estandar, df)

    puntos_curva = [{"x": round(float(vx), 4), "y": round(float(vy), 4)} for vx, vy in zip(rango_x, rango_y)]

    # ZONAS DE RECHAZO
    x_crit_inf = mu_pob + (crit_inf * error_estandar) if crit_inf != -float('inf') else min(rango_x)
    x_crit_sup = mu_pob + (crit_sup * error_estandar) if crit_sup != float('inf') else max(rango_x)

    puntos_aceptacion = list()
    puntos_rechazo_1 = list()
    puntos_rechazo_2 = list()  # <--- NUEVA LISTA PARA LA SEGUNDA COLA

    # SEPARAMOS QUIRÚRGICAMENTE LAS COLAS
    for p in puntos_curva:
        if tipo_prueba == "dos_colas":
            if p['x'] <= x_crit_inf:
                puntos_rechazo_1.append(p)
            elif p['x'] >= x_crit_sup:
                puntos_rechazo_2.append(p)  # <--- Van a la nueva lista
            else:
                puntos_aceptacion.append(p)
        elif tipo_prueba == "cola_izq":
            if p['x'] <= x_crit_inf:
                puntos_rechazo_1.append(p)
            else:
                puntos_aceptacion.append(p)
        elif tipo_prueba == "cola_der":
            if p['x'] >= x_crit_sup:
                puntos_rechazo_1.append(p)
            else:
                puntos_aceptacion.append(p)

    return {
        "tema": f"Prueba de Hipótesis para la Media ({nombre_test})",
        "contexto": contexto,
        "simbolo_estadistico": "P_val",
        "datos_curva": puntos_curva,
        "sombreado_1": puntos_aceptacion,  # Zona Segura (Verde/Teal)
        "sombreado_2": puntos_rechazo_1,  # Cola Izquierda o Única (Roja)
        "sombreado_3": puntos_rechazo_2,  # Cola Derecha (Roja) <--- ¡NUEVO!
        "paciente_x": round(x_barra, 2),
        "paciente_z": round(stat_prueba, 2),
        "percentil": alfa * 100,
        "tipo_area": tipo_prueba,
        "pasos": [
            {
                "paso_num": 1, "titulo": "Paso 1: Plantear Hipótesis",
                "explicacion": f"Asumimos que la media poblacional es {mu_pob} ($H_0$). Nuestra prueba es a {explicacion_h1}",
                "formula_latex": f"H_0: \\mu = {mu_pob} \\quad \\text{{vs}} \\quad {h1_latex}"
            },
            {
                "paso_num": 2, "titulo": "Paso 2: Valor Crítico (La frontera)",
                "explicacion": f"Usando un nivel de significancia $\\alpha={alfa}$ y la distribución {nombre_test}, calculamos dónde empieza la zona de rechazo extrema.",
                "formula_latex": f"{simbolo_stat}_{{crit}} = {str_critico}"
            },
            {
                "paso_num": 3, "titulo": "Paso 3: Estadístico de Prueba (Nuestra Muestra)",
                "explicacion": f"Nuestra muestra arrojó una media de {x_barra}. Calculamos cuántos Errores Estándar (SE={round(error_estandar, 2)}) se alejó del centro.",
                "formula_latex": f"{simbolo_stat}_{{calc}} = \\frac{{{x_barra} - {mu_pob}}}{{{round(error_estandar, 3)}}} = {round(stat_prueba, 3)}"
            },
            {
                "paso_num": 4, "titulo": "Paso 4: El Valor P (P-value)",
                "explicacion": f"El Valor P nos dice la probabilidad de obtener una muestra tan extrema como la nuestra SI la Hipótesis Nula fuera cierta.",
                "formula_latex": f"\\text{{Valor P}} = {round(p_valor, 4)}"
            }
        ],
        "resultado_final": round(p_valor, 4),
        "interpretacion": conclusion_texto
    }
