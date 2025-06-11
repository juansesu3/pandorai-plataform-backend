# app/services/calendar_service.py

from typing import List, Dict

# Simulador de un sistema de calendario (reemplaza esto con Google Calendar o tu backend real)
calendar_db = []

async def get_availability(query: str) -> List[str]:
    # Lógica de ejemplo
    return [
        "2025-06-07 10:00",
        "2025-06-07 11:00",
        "2025-06-07 14:30"
    ]

async def create_event(query: str) -> str:
    calendar_db.append(query)
    return f"Tu cita ha sido agendada con éxito para: {query}"

async def modify_event(query: str) -> str:
    # Simula modificación
    return f"La cita ha sido modificada según: {query}"

async def cancel_event(query: str) -> str:
    # Simula cancelación
    return f"La cita ha sido cancelada según lo solicitado: {query}"
