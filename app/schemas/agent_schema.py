# schemas/agent_schema.py

from typing import Optional, List
from pydantic import BaseModel, Field

class AgentConfig(BaseModel):
    available_days: List[str] = Field(default_factory=lambda: ["Monday", "Tuesday", "Wednesday"])
    hours: str = "09:00-13:00,14:00-18:00"
    interval: int = 30

class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    model: str = "gpt-4-turbo"
    config: AgentConfig = Field(default_factory=AgentConfig)
