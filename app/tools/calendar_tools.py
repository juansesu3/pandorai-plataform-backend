# tools/calendar_tools.py

from datetime import datetime, timedelta
# Asumo que tienes un cliente de Google Calendar ya inicializado, p.ej. `service`
# usando google-api-python-client y credenciales configuradas.

def check_availability_tool(date: str) -> str:
    """
    date: string con formato 'YYYY-MM-DD' o 'YYYY-MM-DDTHH:MM'
    Devuelve un texto con las franjas disponibles para reservar.
    """
    # Parsear la fecha recibida
    fecha_obj = datetime.fromisoformat(date)
    inicio = datetime.combine(fecha_obj.date(), datetime.min.time())
    fin = datetime.combine(fecha_obj.date(), datetime.max.time())
    # Llamada a Google Calendar: freebusy.query
    body = {
        "timeMin": inicio.isoformat() + 'Z',
        "timeMax": fin.isoformat() + 'Z',
        "timeZone": "Europe/Zurich",
        "items": [{"id": "primary"}]  # o el calendarId que uses para citas
    }
    calendar_response = service.freebusy().query(body=body).execute()
    # Extraer busy slots y deducir franjas libres
    busy_slots = calendar_response['calendars']['primary']['busy']
    # [Aquí va la lógica para invertir los busy slots en franjas libres]
    franjas_libres = _calcular_franjas_libres(busy_slots, inicio, fin)
    # Formatear en texto:
    if not franjas_libres:
        return "Lo siento, no hay horarios disponibles para esa fecha."
    texto = "Estos son los horarios libres para el " + fecha_obj.strftime("%d %B %Y") + ":\n"
    for slot in franjas_libres:
        texto += f"- De {slot['start'].strftime('%H:%M')} a {slot['end'].strftime('%H:%M')}\n"
    return texto

def create_appointment_tool(date: str, duration_min: int, user_phone: str) -> str:
    """
    date: fecha/hora deseada en ISO. duration_min: duración en minutos.
    user_phone: número de teléfono para adjuntar como descripción/meta.
    """
    start_dt = datetime.fromisoformat(date)
    end_dt = start_dt + timedelta(minutes=duration_min)
    event_body = {
        "summary": f"Cita con {user_phone}",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Zurich"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Europe/Zurich"},
        "description": f"Cita reservada vía WhatsApp con usuario {user_phone}.",
        # Opcional: reminders por defecto desactivados (usaremos nuestro propio scheduler)
        "reminders": {"useDefault": False},
    }
    event = service.events().insert(calendarId='primary', body=event_body).execute()
    # Guardar en BD local la cita:
    cita_id = event['id']
    _guardar_cita_en_bd(user_phone, cita_id, start_dt, end_dt)
    fecha_str = start_dt.strftime("%d %B %Y a las %H:%M")
    return f"✅ Tu cita ha sido agendada para el {fecha_str}. Tu ID de cita es `{cita_id}`. ¿Deseas algo más?"

def modify_appointment_tool(event_id: str, new_date: str, new_duration: int) -> str:
    """
    Cambia la fecha y/o duración de una cita existente.
    """
    evento = service.events().get(calendarId='primary', eventId=event_id).execute()
    start_dt = datetime.fromisoformat(new_date)
    end_dt = start_dt + timedelta(minutes=new_duration)
    evento['start'] = {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Zurich"}
    evento['end'] = {"dateTime": end_dt.isoformat(), "timeZone": "Europe/Zurich"}
    updated_event = service.events().update(
        calendarId='primary', eventId=event_id, body=evento
    ).execute()
    # Actualizar en BD local
    _actualizar_cita_en_bd(event_id, start_dt, end_dt)
    return f"✏️ Tu cita (ID `{event_id}`) ha sido actualizada al {start_dt.strftime('%d %B %Y a las %H:%M')}."

def cancel_appointment_tool(event_id: str) -> str:
    """
    Cancela una cita existente (la borra o la marca como cancelada).
    """
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    _marcar_cita_como_cancelada(event_id)
    return f"🗑️ Tu cita (ID `{event_id}`) ha sido cancelada. ¡Si necesitas reagendar, házmelo saber!"

# Funciones auxiliares de BD:
def _guardar_cita_en_bd(user_phone, event_id, start_dt, end_dt):
    # Aquí guardas en tu base de datos (PostgreSQL, MySQL, SQLite, etc.)
    pass

def _actualizar_cita_en_bd(event_id, new_start, new_end):
    pass

def _marcar_cita_como_cancelada(event_id):
    pass

def _calcular_franjas_libres(busy_slots, inicio, fin):
    """
    Recibe una lista de busy_slots con dicts {'start': ISO, 'end': ISO}
    y devuelve las franjas libres (lista de dicts {'start': datetime, 'end': datetime}).
    """
    # Simplificación: si no hay busy, el día completo está libre:
    if not busy_slots:
        return [{"start": inicio, "end": fin}]
    # Ordenar busy slots por inicio:
    busy_ordenados = sorted([
        {"start": datetime.fromisoformat(s['start'].replace('Z','+00:00')),
         "end": datetime.fromisoformat(s['end'].replace('Z','+00:00'))}
        for s in busy_slots
    ], key=lambda x: x['start'])
    franjas = []
    cursor = inicio
    for b in busy_ordenados:
        if b['start'] > cursor:
            franjas.append({"start": cursor, "end": b['start']})
        cursor = max(cursor, b['end'])
    if cursor < fin:
        franjas.append({"start": cursor, "end": fin})
    return franjas
