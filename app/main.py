# app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()  # Carga las variables desde el archivo .env

app = FastAPI(
    title="PandorAI Backend",
    description="Backend para gestión de agentes de inteligencia artificial",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al backend de PandorAI"}
