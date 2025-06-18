from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime


class Message(BaseModel):
    sender: Literal["admin", "agent", "user"]
    content: str
    timestamp: datetime


class Conversation(BaseModel):
    _id: Optional[str]  # opcional porque lo genera MongoDB
    agentId: str
    channel: Literal["whatsapp", "web", "email"]
    contactId: str
    messages: List[Message] = []
    createdAt: datetime
    updatedAt: datetime

class Shift(BaseModel):
    start: str  # formato "HH:MM"
    end: str

class WorkingDay(BaseModel):
    day: Literal["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    enabled: bool
    shifts: List[Shift]

class Service(BaseModel):
    name: str
    duration: int  # en minutos
    price: Optional[float] = None
    active: bool = True

class AgentConfiguration(BaseModel):
    agentId: str
    agentName: Optional[str]
    whatsapp: Optional[str]
    services: List[Service] = []
    workingDays: List[WorkingDay] = []
    slotDuration: int = 30
    bufferTime: int = 10
    maxAppointmentsPerDay: int = 10
    allowReschedule: bool = True
    notifyBy: List[Literal["email", "whatsapp", "sms"]] = []
    cancellationPolicy: Optional[str] = ""
    notes: Optional[str] = ""
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
    agentConfigurations: Optional[List[AgentConfiguration]] = []
    conversations: Optional[List[Conversation]] = [] 
    created_at: datetime
