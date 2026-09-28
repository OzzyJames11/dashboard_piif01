# Su única responsabilidad es establecer y devolver la conexión a MongoDB.
# (Capa de Datos - SRP)
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

def get_database():
    """Retorna la instancia de la base de datos MongoDB."""
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB]
