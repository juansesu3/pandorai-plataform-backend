from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional
from app.db.mongo import users_collection
from app.api.auth import get_current_user  # Importamos la función que valida el token

router = APIRouter()

# Configuración de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic model para el registro de usuario
class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    profile_image_url: Optional[str] = None

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: RegisterUser, current_user: dict = Depends(get_current_user)):
    # Verifica si el usuario ya existe
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already exists"
        )

    # Hashea la contraseña
    hashed_password = get_password_hash(user.password)

    # Crea un nuevo usuario
    new_user = {
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password,
        "profile_image_url": user.profile_image_url,
        "created_at": datetime.utcnow()
    }

    # Inserta el usuario en la base de datos
    insert_result = users_collection.insert_one(new_user)
    user_id = insert_result.inserted_id

    return {
        "message": "User created successfully",
        "user_id": str(user_id)
    }