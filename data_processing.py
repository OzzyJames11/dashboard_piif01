# (Lógica de Negocio - SRP)
# Aquí vive Pandas. Se encarga de extraer la data y transformarla (el explode). No sabe nada de Streamlit ni de variables de entorno.
import pandas as pd
from config import EPN_CAREERS

def get_general_metrics(db):
    """Retorna los totales de Bronze (Antes) y Gold (Después) para KPIs y Funnel."""
    total_bronze = db["bronze_jobs"].count_documents({})
    total_gold = db["gold_jobs"].count_documents({})
    
    # Prevenir división por cero si la BD está vacía
    survival_rate = (total_gold / total_bronze * 100) if total_bronze > 0 else 0
    
    return total_bronze, total_gold, survival_rate

def get_source_distribution(db):
    """Agrupa la cantidad de ofertas por fuente (Antes y Después del filtrado)."""
    # Agregación en Bronze (Antes)
    pipeline_bronze = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}]
    bronze_src = list(db["bronze_jobs"].aggregate(pipeline_bronze))
    df_bronze = pd.DataFrame(bronze_src).rename(columns={"_id": "Fuente", "count": "Cantidad"})
    df_bronze["Etapa"] = "1. Antes (Universo Scrapeado)"

    # Agregación en Gold (Después)
    pipeline_gold = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}]
    gold_src = list(db["gold_jobs"].aggregate(pipeline_gold))
    df_gold = pd.DataFrame(gold_src).rename(columns={"_id": "Fuente", "count": "Cantidad"})
    df_gold["Etapa"] = "2. Después (Ofertas Útiles)"

    # Unir ambos DataFrames
    df_sources = pd.concat([df_bronze, df_gold], ignore_index=True)
    # Llenar posibles valores nulos si una fuente no existe
    df_sources['Fuente'] = df_sources['Fuente'].fillna('Desconocida')
    
    return df_sources

def get_careers_distribution(db):
    """Desanida las carreras y fuerza la aparición de las 24 de la EPN."""
    cursor = db["gold_jobs"].find(
        {"carreras_relacionadas": {"$exists": True, "$ne": []}}, 
        {"_id": 0, "carreras_relacionadas": 1}
    )
    
    df = pd.DataFrame(list(cursor))
    
    # Crear un DataFrame base con las 24 carreras obligatorias
    df_all_careers = pd.DataFrame({'Carrera': EPN_CAREERS})
    
    if df.empty:
        df_all_careers['Cantidad de Ofertas'] = 0
        return df_all_careers
        
    # Desanidar (Explode)
    df_exploded = df.explode('carreras_relacionadas').dropna(subset=['carreras_relacionadas'])
    conteo = df_exploded['carreras_relacionadas'].value_counts().reset_index()
    conteo.columns = ['Carrera', 'Cantidad de Ofertas']
    
    # EL TRUCO: Left Join para cruzar nuestra lista fija de 24 con lo que hay en la BD.
    # Lo que no haga match, quedará como NaN y lo rellenamos con 0.
    conteo_final = pd.merge(df_all_careers, conteo, on='Carrera', how='left').fillna(0)
    
    return conteo_final

def generate_analytical_insights(df_sources, total_bronze, total_gold):
    if df_sources.empty or total_bronze == 0:
        return []

    # Separar datos de las etapas
    antes = df_sources[df_sources['Etapa'] == '1. Antes (Universo Scrapeado)'].set_index('Fuente')
    despues = df_sources[df_sources['Etapa'] == '2. Después (Ofertas Útiles)'].set_index('Fuente')
    
    insights = []
    
    # Calcular la tasa de rendimiento (yield) por fuente
    for fuente in antes.index:
        vol_inicial = antes.loc[fuente, 'Cantidad']
        vol_final = despues.loc[fuente, 'Cantidad'] if fuente in despues.index else 0
        
        if vol_inicial > 0:
            tasa = (vol_final / vol_inicial) * 100
            
            # 1. Ruido Alto (< 10%) - Ej: Multitrabajos
            if tasa < 10:
                insights.append(f"**{fuente.capitalize()}**: Aporta el mayor volumen de " 
                                f"ruido ({vol_inicial:,} ofertas crudas), pero su tasa de utilidad "
                                f"para la EPN es sumamente baja ({tasa:.1f}%).")
                                
            # 2. Alta Eficiencia (>= 18%) - Ej: Get on Board
            elif tasa >= 18:
                insights.append(f"**{fuente.capitalize()}**: Es una plataforma de nicho altamente "
                                f"eficiente. El {tasa:.1f}% de sus publicaciones ({vol_final} ofertas) "
                                f"hace match directo con los perfiles de la universidad.")
                                
            # 3. Rendimiento Equilibrado (10% - 18%, Volumen alto) - Ej: Computrabajo
            elif 10 <= tasa < 18 and vol_inicial > (total_bronze * 0.05):
                insights.append(f"**{fuente.capitalize()}**: Mantiene un rendimiento estable. "
                                f"Aporta un volumen inicial considerable ({vol_inicial:,}) con una "
                                f"tasa de conversión aceptable del {tasa:.1f}%.")
                                
            # 4. Fuente Complementaria (10% - 18%, Volumen bajo) - Ej: Talent
            else:
                insights.append(f"**{fuente.capitalize()}**: Tiene una extracción inicial de menor escala "
                                f"({vol_inicial:,} ofertas), pero mantiene una sólida tasa de "
                                f"viabilidad del {tasa:.1f}%, sirviendo como una buena fuente complementaria.")

    return insights

def get_geographic_distribution(db):
    """Extrae las métricas geográficas desde la capa Silver limpiando datos nulos."""
    
    total_silver = db["silver_jobs"].count_documents({})
    
    # 2. Agregación por País (Exigimos que sea un string válido y filtramos basura)
    pipeline_pais = [
        {"$match": {"pais": {"$type": "string", "$nin": ["", " ", "None", "null", "No especificado"]}}},
        {"$group": {"_id": "$pais", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    df_pais = pd.DataFrame(list(db["silver_jobs"].aggregate(pipeline_pais)))
    
    if not df_pais.empty:
        df_pais.rename(columns={"_id": "País", "count": "Ofertas"}, inplace=True)
        # Limpieza de espacios en blanco antes de clasificar
        df_pais['Categoría'] = df_pais['País'].apply(lambda x: 'Ecuador' if str(x).strip().lower() == 'ecuador' else 'Internacional')
        resumen_cat = df_pais.groupby('Categoría')['Ofertas'].sum().reset_index()
    else:
        df_pais = pd.DataFrame(columns=['País', 'Ofertas', 'Categoría'])
        resumen_cat = pd.DataFrame(columns=['Categoría', 'Ofertas'])

    # 3. Agregación por Provincia (Usamos regex sobre 'pais' en lugar de 'pais_iso')
    pipeline_provincia = [
        {"$match": {
            "pais": {"$regex": "^ecuador$", "$options": "i"}, 
            "provincia": {"$type": "string", "$nin": ["", " ", "None", "null", "No especificado"]}
        }},
        {"$group": {"_id": "$provincia", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    df_provincia = pd.DataFrame(list(db["silver_jobs"].aggregate(pipeline_provincia)))
    
    if not df_provincia.empty:
        df_provincia.rename(columns={"_id": "Provincia", "count": "Ofertas"}, inplace=True)
    else:
        df_provincia = pd.DataFrame(columns=['Provincia', 'Ofertas'])

    # 4. Agregación por Ciudad
    pipeline_ciudad = [
        {"$match": {
            "pais": {"$regex": "^ecuador$", "$options": "i"}, 
            "ciudad": {"$type": "string", "$nin": ["", " ", "None", "null", "No especificado"]}
        }},
        {"$group": {"_id": "$ciudad", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    df_ciudad = pd.DataFrame(list(db["silver_jobs"].aggregate(pipeline_ciudad)))
    
    if not df_ciudad.empty:
        df_ciudad.rename(columns={"_id": "Ciudad", "count": "Ofertas"}, inplace=True)
    else:
        df_ciudad = pd.DataFrame(columns=['Ciudad', 'Ofertas'])

    return total_silver, df_pais, resumen_cat, df_provincia, df_ciudad
