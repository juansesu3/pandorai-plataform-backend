# app/models/professional.py

from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Shift(BaseModel):
    start: str  # "HH:MM"
    end: str

class WorkingDay(BaseModel):
    day: Literal["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    enabled: bool
    shifts: List[Shift]

class ProfessionalCreate(BaseModel):
    clientId: str
    name: str
    specialty: str
    shifts: List[WorkingDay] = []

class ProfessionalOut(ProfessionalCreate):
    id: str
