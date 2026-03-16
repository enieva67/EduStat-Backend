#!/bin/bash
# Activar nuestro entorno personalizado
source edustat_env/bin/activate

# Levantar el servidor
echo "Iniciando EduStat Backend..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload