# models/agent.py
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class AgentConfig(BaseModel):
    available_days: List[str] = Field(default_factory=lambda: ["Monday", "Tuesday", "Wednesday"])
    hours: str = "09:00-13:00,14:00-18:00"
    interval: int = 30  # en minutos

class Agent(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    name: str
    description: Optional[str] = None
    model: str = "gpt-4-turbo"
    config: AgentConfig = Field(default_factory=AgentConfig)
    active: bool = True
