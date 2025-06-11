# app/api/v1/routes/websocket_calendar.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.agent_calendar.calenddar_agent_services import CalendarAgentService
from datetime import datetime
import json

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_calendar(websocket: WebSocket):
    await websocket.accept()
    try:
        # Primer mensaje debe contener userUUID
        initial_data = await websocket.receive_text()
        data = json.loads(initial_data)
        session_id = data.get("userUUID", "default_session")
        user_message = data.get("message", "")

        while True:
            result = await CalendarAgentService.generate_answer(user_message, session_id=session_id)
            await websocket.send_text(result["response"])

            next_data = await websocket.receive_text()
            data = json.loads(next_data)
            user_message = data.get("message", "")

    except WebSocketDisconnect:
        print("Cliente desconectado del asistente de calendario")
