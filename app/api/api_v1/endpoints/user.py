from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime
from app.api.auth import get_current_user 

router = APIRouter()

@router.get("/user", response_model=dict)
async def read_user_me(current_user: dict = Depends(get_current_user)):
    # Convertir ObjectId y datetime a string antes de devolver el JSON
    if isinstance(current_user.get("_id"), ObjectId):
        current_user["_id"] = str(current_user["_id"])

    for key, value in current_user.items():
        if isinstance(value, datetime):
            current_user[key] = value.isoformat()

    return JSONResponse(content={"user": current_user})