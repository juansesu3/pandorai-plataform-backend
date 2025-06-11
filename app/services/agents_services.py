# app/services/agents_services.py

from app.db.mongo import agents_collection
from datetime import datetime

async def get_or_create_conversation(agent_name: str, session_id: str):
    """Crea una conversación dentro de un agente si no existe aún."""

    # Verificar si ya existe esa conversación
    agent_doc = await agents_collection.find_one({
        "name": agent_name,
        "conversations.uuid": session_id
    })

    if agent_doc:
        return  # Ya existe, no hacemos nada

    # Si no existe, agregar una nueva conversación vacía
    await agents_collection.update_one(
        {"name": agent_name},
        {
            "$push": {
                "conversations": {
                    "uuid": session_id,
                    "messages": [],
                    "created_at": datetime.utcnow()
                }
            }
        }
    )
