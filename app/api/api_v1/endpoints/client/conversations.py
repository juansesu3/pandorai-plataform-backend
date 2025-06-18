from fastapi import HTTPException,APIRouter
from bson import ObjectId

router = APIRouter()

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    conv = await conversations_collection.find_one({"_id": ObjectId(conversation_id)})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    conv["id"] = str(conv["_id"])
    del conv["_id"]
    return conv