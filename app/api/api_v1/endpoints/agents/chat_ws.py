# app/api/v1/routes/chat_ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

router = APIRouter()

# Guardamos sockets abiertos para cada sesión cliente-agente
active_connections: Dict[str, WebSocket] = {}

@router.websocket("/ws/agents/{agent_id}/chat")
async def chat_ws(websocket: WebSocket, agent_id: str, client_id: str):
    await websocket.accept()
    session_key = f"{client_id}-{agent_id}"
    active_connections[session_key] = websocket

    try:
        while True:
            await websocket.receive_text()  # Puedes recibir mensajes si necesitas
    except WebSocketDisconnect:
        del active_connections[session_key]
        print(f"🔌 WS desconectado: {session_key}")
