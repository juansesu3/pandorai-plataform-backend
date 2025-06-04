from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URI de MongoDB desde las variables de entorno
uri = os.getenv("MONGODB_URI")

if not uri:
    raise Exception("MONGODB_URI not found in environment variables")

# Disable SSL certificate verification (not recommended for production)
client = MongoClient(uri, server_api=ServerApi('1'), tls=True, tlsAllowInvalidCertificates=True)

db = client.pandorai_db
collection = db['pandorai_plat_db']
users_collection = db['users']
