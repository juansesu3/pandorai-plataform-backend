from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
from app.core.config import chats_collection
from app.services.agent_logic import responder_agente

router = APIRouter()
@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_message = await websocket.receive_text()
            ai_response = responder_agente(user_message)
            chats_collection.insert_one({
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow()
            })
            await websocket.send_text(ai_response)
            
    except WebSocketDisconnect:
        print("Cliente desconectado del chat")
