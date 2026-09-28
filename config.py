#  Centraliza la lectura del .env. Cualquier archivo que necesite configuración lo importa de aquí, en lugar de leer el sistema operativo múltiples veces.
# DRY
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "TalentMine")
