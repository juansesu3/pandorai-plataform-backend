from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class ClientCreate(BaseModel):
    companyName: str
    contactName: str
    email: EmailStr
    phone: Optional[str]
    businessType: Optional[str]
    timezone: str
    workingHoursStart: str
    workingHoursEnd: str
    notes: Optional[str] = ""
    agentId: str

class ClientOut(BaseModel):
    id: str
    companyName: str
    contactName: str
    email: str
    phone: Optional[str]
    businessType: Optional[str]
    timezone: str
    workingHoursStart: str
    workingHoursEnd: str
    notes: Optional[str]
    agentIds: List[str]
    created_at: datetime
