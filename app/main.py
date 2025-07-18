#app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.register import router as register_router
from app.api.api_v1.endpoints import user
from app.api.api_v1.endpoints import agent
from app.api.api_v1.endpoints.agents import chat_ws
from app.api.api_v1.endpoints.client import client
from app.api.api_v1.endpoints.client import messages
from app.api.api_v1.endpoints.client import professionals
app = FastAPI()

# Configuración del middleware de CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://pandorai.ch",
    "https://pandorai-admin-v2.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
) 

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(register_router, prefix="/register", tags=["register"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(agent.router, prefix="/agents", tags=["agents"])
app.include_router(client.router, prefix="/clients", tags=["clients"])
app.include_router(chat_ws.router)
app.include_router(messages.router, prefix="/messages", tags=["messages"])  # <-- agrega esto si no lo tenías
app.include_router(professionals.router, tags=["professionals"])
@app.get("/")
async def homepage():
    return {"message": "Hello World"}