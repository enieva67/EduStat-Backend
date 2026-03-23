import io
import base64
import numpy as np
import math
import matplotlib.pyplot as plt


def clean_data_for_json(data):
    """
    Escudo definitivo anti-crashes de JSON.
    Traduce objetos de NumPy y limpia los NaN/Infinity para que Flutter no explote.
    """
    # 1. Detectar y traducir enteros de NumPy
    if isinstance(data, (np.integer, np.int64, np.int32)):
        return int(data)

    # 2. Detectar y traducir decimales de NumPy
    if isinstance(data, (np.floating, np.float64, np.float32)):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)

    # 3. Limpiar floats nativos corruptos
    if isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
        return None

    # 4. Magia recursiva para bucear por diccionarios y listas
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_data_for_json(i) for i in data]

    return data


def fig_to_base64(fig):
    """
    REGLA: Convertir figura a Base64 y destruir la figura de la RAM.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")

    # MUY IMPORTANTE: Liberar memoria para evitar Out Of Memory (OOM)
    fig.clf()
    plt.close(fig)

    return img_str