import matplotlib

# REGLA ESTRICTA: Evita crashes en Linux si no hay entorno gráfico
matplotlib.use('Agg')

# Configuraciones globales del backend
APP_NAME = "EduStat Backend"
VERSION = "1.0.0"