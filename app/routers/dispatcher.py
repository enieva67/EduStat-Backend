import asyncio

from app.services.estadistica.curva_normal import calcular_puntaje_z_y_curva, calcular_x_desde_area
from app.services.estadistica.moda import calcular_moda_paso_a_paso, calcular_moda_datos_agrupados
from app.services.estadistica.variabilidad import calcular_varianza_paso_a_paso, calcular_varianza_datos_agrupados
from app.utils.formatters import clean_data_for_json
from app.services.estadistica.correlacion import calcular_pearson_paso_a_paso
from app.services.estadistica.correlacion import calcular_spearman_paso_a_paso
from app.services.estadistica.correlacion import calcular_phi_paso_a_paso
from app.services.estadistica.inferencia import calcular_intervalo_confianza_media
from app.services.estadistica.inferencia import (
    calcular_intervalo_confianza_media,
    calcular_prueba_hipotesis_media) # <--- NUEVA
from app.services.estadistica.chi_cuadrado import calcular_chi2_bondad, calcular_chi2_independencia
# IMPORTAMOS NUESTRO NUEVO MOTOR DIDÁCTICO
from app.services.estadistica.tendencia_central import calcular_media_paso_a_paso, calcular_media_datos_agrupados, \
    calcular_percentil_paso_a_paso, calcular_percentil_datos_agrupados
from app.services.data_manager.file_reader import procesar_archivo_base64

from app.services.estadistica.tendencia_central import calcular_mediana_paso_a_paso      # NUEVO
from app.services.estadistica.tendencia_central import calcular_mediana_datos_agrupados   # NUEVO

def procesar_diagnostico(parametros: dict) -> dict:
    return {
        "mensaje": "¡Conexión estable con EduStat Backend!",
        "version_python": "3.12",
        "estado": "Operativo"
    }


async def dispatch_message(payload: dict) -> dict:
    req_id = payload.get("id", None)
    accion = payload.get("accion", "desconocida")
    parametros = payload.get("parametros", {})

    respuesta = {"id": req_id, "estado": "error", "datos": None, "imagen": None}

    try:
        if accion == "diagnostico":
            datos_crudos = await asyncio.to_thread(procesar_diagnostico, parametros)
            respuesta["estado"] = "exito"
            respuesta["datos"] = datos_crudos

        # NUEVA ACCIÓN: Calcular la Media
        elif accion == "calcular_media_sin_agrupar":
            # Extraemos los datos que nos mandará Flutter
            datos_lista = parametros.get("datos", [])
            contexto_texto = parametros.get("contexto", "Datos genéricos")

            # Mandamos a calcular a otro hilo para no bloquear el servidor
            datos_crudos = await asyncio.to_thread(calcular_media_paso_a_paso, datos_lista, contexto_texto)

            respuesta["estado"] = "exito"
            respuesta["datos"] = datos_crudos
        # NUEVA ACCIÓN: Calcular la Media Agrupada
        elif accion == "calcular_media_agrupada":
            # Extraemos los datos que nos mandará Flutter
            clases_lista = parametros.get("clases", [])
            contexto_texto = parametros.get("contexto", "Datos genéricos agrupados")

            # Mandamos a calcular a otro hilo
            datos_crudos = await asyncio.to_thread(calcular_media_datos_agrupados, clases_lista, contexto_texto)

            respuesta["estado"] = "exito"
            respuesta["datos"] = datos_crudos
            # NUEVA ACCIÓN: Leer archivo Excel/CSV
        elif accion == "procesar_archivo":
            contenido_b64 = parametros.get("base64", "")
            nombre_archivo = parametros.get("nombre", "datos.csv")

            datos_crudos = await asyncio.to_thread(procesar_archivo_base64, contenido_b64, nombre_archivo)

            respuesta["estado"] = "exito"
            respuesta["datos"] = datos_crudos
            # NUEVA ACCIÓN: Mediana Sin Agrupar
        elif accion == "calcular_mediana_sin_agrupar":
            datos_lista = parametros.get("datos", [])
            contexto_texto = parametros.get("contexto", "Datos genéricos")
            datos_crudos = await asyncio.to_thread(calcular_mediana_paso_a_paso, datos_lista, contexto_texto)
            respuesta["estado"] = "exito"
            respuesta["datos"] = datos_crudos

        # NUEVA ACCIÓN: Mediana Agrupada
        elif accion == "calcular_mediana_agrupada":
            clases_lista = parametros.get("clases", [])
            contexto_texto = parametros.get("contexto", "Datos genéricos")
            datos_crudos = await asyncio.to_thread(calcular_mediana_datos_agrupados, clases_lista, contexto_texto)
            respuesta["estado"] = "exito"
            respuesta["datos"] = datos_crudos
        elif accion == "calcular_varianza_sin_agrupar":
            datos_crudos = await asyncio.to_thread(calcular_varianza_paso_a_paso, parametros.get("datos", []),
                                                   parametros.get("contexto", ""))
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
        elif accion == "calcular_varianza_agrupada":
            datos_crudos = await asyncio.to_thread(calcular_varianza_datos_agrupados, parametros.get("clases", []),
                                                   parametros.get("contexto", ""))
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
        elif accion == "calcular_moda_sin_agrupar":
            datos_crudos = await asyncio.to_thread(calcular_moda_paso_a_paso, parametros.get("datos", []),
                                                   parametros.get("contexto", ""))
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos

        elif accion == "calcular_moda_agrupada":
            datos_crudos = await asyncio.to_thread(calcular_moda_datos_agrupados, parametros.get("clases", []),
                                                   parametros.get("contexto", ""))
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
        elif accion == "calcular_percentil_sin_agrupar":
            k_val = int(parametros.get("k", 50))  # Extraemos el percentil que quiere el usuario
            datos_crudos = await asyncio.to_thread(calcular_percentil_paso_a_paso, parametros.get("datos", []),
                                                   parametros.get("contexto", ""), k_val)
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos

        elif accion == "calcular_percentil_agrupada":
            k_val = int(parametros.get("k", 50))
            datos_crudos = await asyncio.to_thread(calcular_percentil_datos_agrupados, parametros.get("clases", []),
                                                   parametros.get("contexto", ""), k_val)
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
            # NUEVA ACCIÓN: Puntaje Z y Áreas
        elif accion == "calcular_puntaje_z":
            media = float(parametros.get("media", 100))
            desviacion = float(parametros.get("desviacion", 15))
            x_val = float(parametros.get("x", 115))
            tipo_area = parametros.get("tipo_area", "menor")

            # Extraemos x2 (puede ser None si no lo mandan)
            x2_val_raw = parametros.get("x2")
            x2_val = float(x2_val_raw) if x2_val_raw is not None else None

            datos_crudos = await asyncio.to_thread(calcular_puntaje_z_y_curva, media, desviacion, x_val, tipo_area,
                                                   x2_val, "Puntaje")
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
            # NUEVA ACCIÓN: Proceso Inverso (Área a X)
        elif accion == "calcular_x_desde_area":
            media = float(parametros.get("media", 100))
            desviacion = float(parametros.get("desviacion", 15))
            area1_val = float(parametros.get("area1", 95))
            tipo_area = parametros.get("tipo_area", "menor")

            area2_raw = parametros.get("area2")
            area2_val = float(area2_raw) if area2_raw is not None else None

            datos_crudos = await asyncio.to_thread(calcular_x_desde_area, media, desviacion, area1_val, tipo_area,
                                                   area2_val, "Paciente")
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
            # NUEVAS ACCIONES: CORRELACIONES (Bivariadas)
        elif accion == "calcular_pearson":
            x = parametros.get("x", [])
            y = parametros.get("y", [])
            ctx_x = parametros.get("ctx_x", "Variable X")
            ctx_y = parametros.get("ctx_y", "Variable Y")
            datos_crudos = await asyncio.to_thread(calcular_pearson_paso_a_paso, x, y, ctx_x, ctx_y)
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos

        elif accion == "calcular_spearman":
            x = parametros.get("x", [])
            y = parametros.get("y", [])
            ctx_x = parametros.get("ctx_x", "Variable X")
            ctx_y = parametros.get("ctx_y", "Variable Y")
            datos_crudos = await asyncio.to_thread(calcular_spearman_paso_a_paso, x, y, ctx_x, ctx_y)
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos

        elif accion == "calcular_phi":
            x = parametros.get("x", [])
            y = parametros.get("y", [])
            ctx_x = parametros.get("ctx_x", "Variable X")
            ctx_y = parametros.get("ctx_y", "Variable Y")
            datos_crudos = await asyncio.to_thread(calcular_phi_paso_a_paso, x, y, ctx_x, ctx_y)
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
            # NUEVA ACCIÓN: INFERENCIA (Intervalos de Confianza)
        elif accion == "calcular_intervalo_confianza":
            media = float(parametros.get("media", 100))
            desviacion = float(parametros.get("desviacion", 15))
            n = int(parametros.get("n", 30))
            confianza = float(parametros.get("confianza", 95.0))

            datos_crudos = await asyncio.to_thread(calcular_intervalo_confianza_media, media, desviacion, n, confianza,
                                                   "Variable")
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
            # NUEVA ACCIÓN: Pruebas de Hipótesis
        elif accion == "calcular_prueba_hipotesis":
            mu_pob = float(parametros.get("mu_pob", 100))
            x_barra = float(parametros.get("x_barra", 105))
            desviacion = float(parametros.get("desviacion", 15))
            n = int(parametros.get("n", 30))
            alfa = float(parametros.get("alfa", 0.05))
            tipo_prueba = parametros.get("tipo_prueba", "dos_colas")

            datos_crudos = await asyncio.to_thread(calcular_prueba_hipotesis_media, mu_pob, x_barra, desviacion, n,
                                                   alfa, tipo_prueba, "Variable")
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
            # NUEVAS ACCIONES: JI-CUADRADO (Categóricas)
        elif accion == "calcular_chi2_bondad":
            datos = parametros.get("datos", [])
            esperadas = parametros.get("esperadas")  # Puede ser None
            tipo_ingreso = parametros.get("tipo_ingreso", "frecuencias")
            alfa = float(parametros.get("alfa", 0.05))

            datos_crudos = await asyncio.to_thread(calcular_chi2_bondad, datos, esperadas, tipo_ingreso, alfa,
                                                   "Categorías")
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos

        elif accion == "calcular_chi2_independencia":
            matriz = parametros.get("matriz", [])
            raw_x = parametros.get("raw_x", [])
            raw_y = parametros.get("raw_y", [])
            tipo_ingreso = parametros.get("tipo_ingreso", "tabla")
            alfa = float(parametros.get("alfa", 0.05))

            datos_crudos = await asyncio.to_thread(calcular_chi2_independencia, matriz, raw_x, raw_y, tipo_ingreso,
                                                   alfa, "Variables")
            respuesta["estado"], respuesta["datos"] = "exito", datos_crudos
        else:
            respuesta["estado"] = "error"
            respuesta["datos"] = {"mensaje": f"Acción '{accion}' no soportada."}

    except Exception as e:
        respuesta["estado"] = "error"
        respuesta["datos"] = {"mensaje": f"Error interno: {str(e)}"}

    respuesta["datos"] = clean_data_for_json(respuesta["datos"])

    return respuesta