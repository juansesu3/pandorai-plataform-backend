# app/api/v1/routes/messages.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
import json
from app.api.api_v1.endpoints.agents.chat_ws import active_connections
from app.db.mongo import conversations_collection
from app.services.agent_calendar.calenddar_agent_services import CalendarAgentService 
router = APIRouter()

class MessageIn(BaseModel):
    sender: str  # 'admin' o 'user'
    content: str
    timestamp: str

@router.post("/clients/{client_id}/agents/{agent_id}/messages")
async def post_message(client_id: str, agent_id: str, msg: MessageIn):
    session_key = f"{client_id}-{agent_id}"

    # Buscar o crear la conversación
    conv = await conversations_collection.find_one({
        "clientId": client_id,
        "agentId": agent_id
    })

    if not conv:
        new_conv = {
            "clientId": client_id,
            "agentId": agent_id,
            "contactId": "admin",  # si quieres puedes incluir más info
            "channel": "admin-panel",
            "messages": [],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        result = await conversations_collection.insert_one(new_conv)
        conv_id = result.inserted_id
    else:
        conv_id = conv["_id"]

    # Agregar mensaje
    new_message = {
        "sender": msg.sender,
        "content": msg.content,
        "timestamp": msg.timestamp,
    }

    await conversations_collection.update_one(
        {"_id": ObjectId(conv_id)},
        {
            "$push": {"messages": new_message},
            "$set": {"updatedAt": datetime.utcnow()}
        }
    )
      # 🧠 Aquí viene la magia: llama a la IA
    ai_response = await CalendarAgentService.generate_answer(
        question=msg.content,
        client_id=client_id,
        agent_id=agent_id,
        contact_id=msg.sender  # o el ID real del contacto si lo tienes
    )
    # Agrega la respuesta a la conversación
    agent_message = {
        "sender": "agent",
        "content": ai_response["response"],
        "timestamp": datetime.utcnow().isoformat()
    }

    await conversations_collection.update_one(
        {"_id": ObjectId(conv_id)},
        {
            "$push": {"messages": agent_message},
            "$set": {"updatedAt": datetime.utcnow()}
        }
    )

    # Enviar por WebSocket si el agente está conectado
    # Enviar al frontend por WebSocket
    if session_key in active_connections:
        ws = active_connections[session_key]
        await ws.send_text(json.dumps({
            "response": ai_response["response"],
            "from": "agent",
            "timestamp": agent_message["timestamp"]
        }))

    return {
        "status": "ok",
        "agentMessage": agent_message
    }
