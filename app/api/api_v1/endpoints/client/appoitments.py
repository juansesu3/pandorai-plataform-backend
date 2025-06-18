# app/api/api_v1/endpoints/appointments.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.agent_calendar.appointments_service import create_appointment

router = APIRouter()


class AppointmentCreate(BaseModel):
    clientId: str
    professionalId: str
    date: str
    time: str
    duration: int
    userInfo: dict


@router.post("/appointments")
async def create(data: AppointmentCreate):
    appointment = await create_appointment(data.dict())
    return {"status": "ok", "appointment": appointment}
