#  Centraliza la lectura del .env. Cualquier archivo que necesite configuración lo importa de aquí, en lugar de leer el sistema operativo múltiples veces.
# DRY
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "TalentMine")

# LISTA MAESTRA DE CARRERAS DE LA EPN
# Debes completar esta lista con los nombres EXACTOS tal cual se guardan en la BD
# para que el cruce de datos identifique cuál tiene 0.
EPN_CAREERS = [
    "Administración de Empresas",
    "Agroindustria",
    "Ciencia de Datos",
    "Computación",
    "Economía",
    "Electricidad",
    "Electrónica y Automatización",
    "Física",
    "Geología",
    "Ingeniería Ambiental",
    "Ingeniería Civil",
    "Ingeniería de la Producción",
    "Ingeniería Química",
    "Inteligencia Artificial",
    "Matemática",
    "Matemática Aplicada",
    "Materiales",
    "Mecánica",
    "Mecatrónica",
    "Petróleos",
    "Sistemas de Información",
    "Software",
    "Tecnologías de la Información",
    "Telecomunicaciones",
]