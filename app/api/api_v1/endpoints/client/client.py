from fastapi import APIRouter, HTTPException, status, Path, Body
from bson import ObjectId
from datetime import datetime
from typing import List
from app.schemas.client_schema import ClientCreate, ClientOut, AgentConfiguration
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

@router.get("/{client_id}/agents")
async def get_agents_by_client(client_id: str):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="ID de cliente inválido")

    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    agent_ids = client.get("agentIds", [])
    if not agent_ids:
        return []

    # Convertir los IDs de agente a ObjectId para la consulta
    object_ids = [ObjectId(aid) for aid in agent_ids if ObjectId.is_valid(aid)]

    cursor = agents_collection.find({"_id": {"$in": object_ids}})
    agents = []
    async for agent in cursor:
        agent["id"] = str(agent["_id"])
        del agent["_id"]
        agents.append(agent)

    return agents

@router.patch("/{client_id}/agents/{agent_id}/configuration")
async def update_agent_configuration_for_client(
    client_id: str,
    agent_id: str,
    config: AgentConfiguration = Body(...)
):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="ID de cliente inválido")

    if client_id != config.agentId:
        # opcional: verificación si el config.agentId debería coincidir con path
        pass

    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Inicializa si no existe
    existing_configs = client.get("agentConfigurations", [])

    # Busca si ya hay configuración para este agente
    updated = False
    for i, ac in enumerate(existing_configs):
        if ac["agentId"] == agent_id:
            existing_configs[i] = config.dict()
            updated = True
            break

    if not updated:
        existing_configs.append(config.dict())

    # Guardar en base de datos
    await clients_collection.update_one(
        {"_id": ObjectId(client_id)},
        {"$set": {"agentConfigurations": existing_configs}}
    )

    return {
        "message": "Configuración del agente actualizada exitosamente",
        "agentId": agent_id
    }