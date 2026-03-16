# Archivo: app/services/data_manager/file_reader.py
import io
import base64
import pandas as pd


def procesar_archivo_base64(contenido_b64: str, nombre_archivo: str) -> dict:
    """
    Recibe un archivo en Base64 desde Flutter, lo lee con Pandas,
    limpia los datos y devuelve las columnas numéricas.
    """
    try:
        # 1. Decodificar el archivo
        file_bytes = base64.b64decode(contenido_b64)
        buffer = io.BytesIO(file_bytes)

        # 2. Leer con Pandas dependiendo de la extensión
        if nombre_archivo.lower().endswith('.csv'):
            df = pd.read_csv(buffer)
        elif nombre_archivo.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(buffer)
        else:
            raise ValueError("Formato no soportado. Usa .csv o .xlsx")

        # 3. Filtrar solo columnas numéricas (La estadística descriptiva requiere números)
        df_numerico = df.select_dtypes(include=['number'])

        if df_numerico.empty:
            raise ValueError("No se encontraron columnas numéricas en el archivo.")

        # 4. Limpiar NaNs y preparar el diccionario para Flutter
        columnas_data = {}
        for col in df_numerico.columns:
            # Eliminamos los valores nulos (celdas vacías) solo de esta columna
            datos_limpios = df_numerico[col].dropna().tolist()
            # Solo enviamos columnas que tengan al menos 1 dato válido
            if len(datos_limpios) > 0:
                columnas_data[col] = datos_limpios

        return {
            "nombre_archivo": nombre_archivo,
            "total_filas_originales": len(df),
            "columnas_disponibles": list(columnas_data.keys()),
            "datos_por_columna": columnas_data,
            "mensaje": f"¡Éxito! Se encontraron {len(columnas_data)} variables numéricas."
        }

    except Exception as e:
        raise Exception(f"Error al leer el archivo: {str(e)}")