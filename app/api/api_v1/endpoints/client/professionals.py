
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from app.db.mongo import professionals_collection, clients_collection
from app.models.professionals import ProfessionalCreate, ProfessionalOut

router = APIRouter()

def to_obj(pro):
    pro['id'] = str(pro['_id'])
    del pro['_id']
    return pro

@router.post("/clients/{client_id}/professionals", response_model=ProfessionalOut)
async def create_professional(client_id: str, data: ProfessionalCreate):
    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    doc = data.dict()
    doc["clientId"] = client_id  # Asociamos manualmente
    result = await professionals_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return to_obj(doc)

@router.get("/clients/{client_id}/professionals", response_model=List[ProfessionalOut])
async def list_professionals(client_id: str):
    professionals = await professionals_collection.find({"clientId": client_id}).to_list(length=100)
    return [to_obj(p) for p in professionals]

@router.get("/professionals/{pro_id}", response_model=ProfessionalOut)
async def get_professional(pro_id: str):
    pro = await professionals_collection.find_one({"_id": ObjectId(pro_id)})
    if not pro:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")
    return to_obj(pro)
