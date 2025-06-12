from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime
from typing import List
from app.schemas.client_schema import ClientCreate, ClientOut
from app.db.mongo import clients_collection, agents_collection

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client(client: ClientCreate):
    # Verifica si el agente existe
    agent = await agents_collection.find_one({"_id": ObjectId(client.agentId)})
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    new_client = {
        "companyName": client.companyName,
        "contactName": client.contactName,
        "email": client.email,
        "phone": client.phone,
        "businessType": client.businessType,
        "timezone": client.timezone,
        "workingHoursStart": client.workingHoursStart,
        "workingHoursEnd": client.workingHoursEnd,
        "notes": client.notes,
        "agentIds": [client.agentId],  # Puedes extenderlo luego
        "created_at": datetime.utcnow()
    }

    result = await clients_collection.insert_one(new_client)

    # Actualiza el agente con el cliente
    await agents_collection.update_one(
        {"_id": ObjectId(client.agentId)},
        {"$addToSet": {"clientIds": str(result.inserted_id)}}
    )

    return {
        "message": "Cliente integrado exitosamente",
        "client_id": str(result.inserted_id)
    }


@router.get("/", response_model=List[ClientOut])
async def get_all_clients():
    cursor = clients_collection.find()
    clients = []
    async for client in cursor:
        client["id"] = str(client["_id"])
        del client["_id"]
        clients.append(client)
    return clients

@router.get("/{client_id}", response_model=ClientOut)
async def get_client_by_id(client_id: str = Path(..., description="ID del cliente")):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="ID de cliente inválido")

    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    client["id"] = str(client["_id"])
    del client["_id"]
    return client