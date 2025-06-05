# api/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.core.config import chats_collection  # MongoDB collection
from bson import ObjectId

router = APIRouter()

class ChatMessage(BaseModel):
    agent_id: str
    user_message: str

@router.post("/chat")
async def send_message(payload: ChatMessage):
    # Aquí iría la lógica del agente de AI
    ai_response = tu_modelo_de_ia(payload.user_message)

    # Guarda en la base de datos
    chats_collection.insert_one({
        "agent_id": ObjectId(payload.agent_id),
        "user_message": payload.user_message,
        "ai_response": ai_response,
        "timestamp": datetime.utcnow()
    })

    return {"response": ai_response}
