# app/db/mongo.py

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

uri = os.getenv("MONGODB_URI")

if not uri:
    raise Exception("MONGODB_URI not found in environment variables")

# Crear cliente asíncrono de MongoDB
client = AsyncIOMotorClient(uri, tls=True, tlsAllowInvalidCertificates=True)

db = client.pandorai_db
collection = db['pandorai_plat_db']
users_collection = db['users']
agents_collection = db['agents']
chats_collection = db['chats']
