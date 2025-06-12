# schemas/agent_schema.py

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime



class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    model: str = "gpt-4-turbo"
    prompt: str = ""
    temperature: float = 0.7
    max_token: int = 1000
    language: str = "es"
    speciality: Optional[str] = None



class AgentOut(AgentCreate):
    id: str
    clientIds: List[str]
    created_at: Optional[datetime] = None