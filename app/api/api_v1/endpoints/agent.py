# api/agent.py

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.api.auth import get_current_user
from app.schemas.agent_schema import AgentCreate
from app.core.config import agents_collection  # MongoDB collection

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate,):
    # Validación básica (opcional): ¿ya hay un agente con ese nombre para este usuario?
    existing =  agents_collection.find_one({
        
        "name": agent.name
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with that name already exists"
        )

    # Crear el nuevo agente
    new_agent = {
        "name": agent.name,
        "description": agent.description,
        "model": agent.model,
        "config": agent.config.dict(),
        "active": True,
        "created_at": datetime.utcnow()
    }

    result =  agents_collection.insert_one(new_agent)

    return {
        "message": "Agent created successfully",
        "agent_id": str(result.inserted_id)
    }
