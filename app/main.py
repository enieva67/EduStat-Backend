import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Importar configuración gatilla matplotlib.use('Agg') desde el inicio
from app.core import config
from app.core.ws_manager import ConnectionManager
from app.routers.dispatcher import dispatch_message

app = FastAPI(title=config.APP_NAME, version=config.VERSION)
manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 1. Escuchar a Flutter
            text_data = await websocket.receive_text()

            # 2. Validar JSON
            try:
                payload = json.loads(text_data)
            except json.JSONDecodeError:
                await manager.send_json({
                    "id": None,
                    "estado": "error",
                    "datos": {"mensaje": "Payload inválido"}
                }, websocket)
                continue

            # 3. Despachar al Router
            respuesta = await dispatch_message(payload)

            # 4. Enviar respuesta
            await manager.send_json(respuesta, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error fatal: {e}")
        manager.disconnect(websocket)