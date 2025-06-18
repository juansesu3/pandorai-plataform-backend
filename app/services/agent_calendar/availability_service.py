from datetime import datetime, timedelta
from typing import List
from app.db.mongo import appointments_collection, professionals_collection
from fastapi import HTTPException

def str_to_time(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

def time_to_str(dt: datetime) -> str:
    return dt.strftime("%H:%M")

async def get_available_slots(professional_name: str, date: str, duration: int = 30) -> List[str]:
    """
    Calcula todos los horarios disponibles para un profesional en un día específico.

    Args:
        professional_name (str): Nombre del profesional
        date (str): Fecha en formato YYYY-MM-DD
        duration (int): Duración de la cita en minutos

    Returns:
        List[str]: Lista de horarios disponibles en formato HH:MM
    """

    # Obtener profesional
    pro = await professionals_collection.find_one({"name": professional_name})
    if not pro:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    # Verificar turnos habilitados ese día
    EN_ES_DAYS = {
    "monday": "lunes",
    "tuesday": "martes",
    "wednesday": "miércoles",
    "thursday": "jueves",
    "friday": "viernes",
    "saturday": "sábado",
    "sunday": "domingo"
    }
    day_en = datetime.strptime(date, "%Y-%m-%d").strftime("%A").lower()
    day_name = EN_ES_DAYS.get(day_en)
    day_config = next(
        (d for d in pro.get("shifts", []) if d["day"].lower() == day_name and d["enabled"]),
        None
    )
    if not day_config:
        return []  # No trabaja ese día

    # Obtener citas ya reservadas
    reserved = await appointments_collection.find({
        "professionalName": professional_name,
        "date": date,
        "status": {"$in": ["confirmed", "pending"]}
    }).to_list(None)

    reserved_times = set(r["time"] for r in reserved)

    # Generar slots disponibles
    available_slots = []
    for shift in day_config["shifts"]:
        start_dt = str_to_time(date, shift["start"])
        end_dt = str_to_time(date, shift["end"])

        while (start_dt + timedelta(minutes=duration)) <= end_dt:
            slot_str = time_to_str(start_dt)
            if slot_str not in reserved_times:
                available_slots.append(slot_str)
            start_dt += timedelta(minutes=duration)

    return available_slots
