# api/agent.py

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from app.api.auth import get_current_user
from app.schemas.agent_schema import AgentCreate, AgentOut
from app.db.mongo import agents_collection  # MongoDB collection
from bson import ObjectId
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate):
    existing = await agents_collection.find_one({
        "name": agent.name
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with that name already exists"
        )

    new_agent = {
        "speciality": agent.speciality,
        "name": agent.name,
        "description": agent.description,
        "prompt": agent.prompt,
        "model": agent.model,
        "temperature": agent.temperature,
        "max_token": agent.max_token,
        "language": agent.language,
        "created_at": datetime.utcnow()
    }

    result = await agents_collection.insert_one(new_agent)

    return {
        "message": "Agent created successfully",
        "agent_id": str(result.inserted_id)
    }
    
@router.get("/", response_model=List[AgentOut])
async def get_all_agents():
    agents_cursor = agents_collection.find()
    agents = []
    async for agent in agents_cursor:
        agent["id"] = str(agent["_id"])
        del agent["_id"]
        agents.append(agent)
    return agents


# 🔹 GET agent by ID
@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent_by_id(agent_id: str):
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID")

    agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent["id"] = str(agent["_id"])
    del agent["_id"]
    return agent
