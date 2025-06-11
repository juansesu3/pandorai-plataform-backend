# models/agent.py
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime



class Agent(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    speciality: Optional[str] = None
    name: str
    description: Optional[str] = None
    model: str = "gpt-4-turbo"
    prompt: str = ""
    temperature: float = 0.7
    max_token: int = 1000
    language: str = "es"
    created_at: datetime
    updated_at: datetime
