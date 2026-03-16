import io
import base64
import math
import matplotlib.pyplot as plt


def clean_data_for_json(data):
    """
    REGLA: Dart crashea con 'NaN' o 'Infinity' en JSON.
    Esta función recursiva los convierte en None (que en JSON es 'null').
    """
    if isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
        return None
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