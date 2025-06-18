# app/services/appointments_service.py

from datetime import datetime, timedelta
from app.db.mongo import professionals_collection, appointments_collection
from fastapi import HTTPException
import pytz


async def create_appointment(data: dict) -> dict:
    """
    Crea una cita si está disponible.
    data = {
        "clientId": str,
        "professionalId": str,
        "date": "YYYY-MM-DD",
        "time": "HH:MM",
        "duration": int,
        "userInfo": { "name": str, "contact": str }
    }
    """
    client_id = data["clientId"]
    professional_id = data["professionalId"]
    date = data["date"]
    time = data["time"]
    duration = data.get("duration", 30)

    # 1. Obtener profesional
    pro = await professionals_collection.find_one({"_id": professional_id})
    if not pro:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    # 2. Verificar si ese día tiene habilitado turno
    day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%A").lower()

    day_config = next(
        (d for d in pro.get("shifts", []) if d["day"].lower() == day_name and d["enabled"]),
        None
    )
    if not day_config:
        raise HTTPException(status_code=400, detail=f"{pro['name']} no trabaja los {day_name}")

    # 3. Validar si ese horario está dentro de los turnos
    slot_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    slot_end = slot_time + timedelta(minutes=duration)

    in_shift = False
    for shift in day_config["shifts"]:
        start = datetime.strptime(f"{date} {shift['start']}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{date} {shift['end']}", "%Y-%m-%d %H:%M")
        if start <= slot_time and slot_end <= end:
            in_shift = True
            break

    if not in_shift:
        raise HTTPException(status_code=400, detail="Horario fuera del turno del profesional")

    # 4. Verificar colisión
    conflict = await appointments_collection.find_one({
        "professionalId": professional_id,
        "date": date,
        "status": {"$in": ["confirmed", "pending"]},
        "time": time  # ← podrías hacer mejor validación con rango también
    })

    if conflict:
        raise HTTPException(status_code=400, detail="Ese horario ya está reservado")

    # 5. Crear cita
    appointment = {
        "clientId": client_id,
        "professionalId": professional_id,
        "userInfo": data["userInfo"],
        "date": date,
        "time": time,
        "duration": duration,
        "status": "confirmed",
        "createdAt": datetime.utcnow()
    }

    result = await appointments_collection.insert_one(appointment)
    appointment["_id"] = result.inserted_id
    return appointment
