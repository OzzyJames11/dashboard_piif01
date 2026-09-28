# (Lógica de Negocio - SRP)
# Aquí vive Pandas. Se encarga de extraer la data y transformarla (el explode). No sabe nada de Streamlit ni de variables de entorno.
import pandas as pd

def get_layer_counts(db):
    """Retorna el total de documentos en las capas Bronze, Silver y Gold."""
    t_bronze = db["bronze_jobs"].count_documents({})
    t_silver = db["silver_jobs"].count_documents({})
    t_gold = db["gold_jobs"].count_documents({})
    return t_bronze, t_silver, t_gold

def get_careers_distribution(db):
    """Extrae y desanida el arreglo de carreras para el conteo final."""
    cursor = db["gold_jobs"].find(
        {"carreras_relacionadas": {"$exists": True, "$ne": []}}, 
        {"_id": 0, "carreras_relacionadas": 1}
    )
    
    df = pd.DataFrame(list(cursor))
    
    if df.empty:
        return pd.DataFrame(columns=['Carrera', 'Cantidad de Ofertas'])
        
    # Lógica de desanidado (Explode) y conteo
    df_exploded = df.explode('carreras_relacionadas').dropna(subset=['carreras_relacionadas'])
    conteo = df_exploded['carreras_relacionadas'].value_counts().reset_index()
    conteo.columns = ['Carrera', 'Cantidad de Ofertas']
    
    return conteo
