# (Capa de Presentación - SRP)
# Es el punto de entrada de Streamlit. Solo se encarga de dibujar la interfaz, utilizando el caché de Streamlit para no golpear la base de datos en cada clic.
import streamlit as st
import plotly.express as px
from database import get_database
from data_processing import get_layer_counts, get_careers_distribution

# Configuración inicial de Streamlit
st.set_page_config(page_title="Dashboard Observatorio Laboral", layout="wide")

# --- Caché y Carga de Datos ---
@st.cache_resource
def init_db():
    return get_database()

@st.cache_data(ttl=3600)
def load_dashboard_data():
    db = init_db()
    counts = get_layer_counts(db)
    careers_df = get_careers_distribution(db)
    return counts, careers_df

# --- Ejecución ---
(total_bronze, total_silver, total_gold), conteo_carreras = load_dashboard_data()

# --- Interfaz Visual ---
st.title("📊 Observatorio Laboral - Análisis de Ofertas")
st.markdown("Análisis descriptivo de los datos procesados en la capa Gold.")

col1, col2, col3 = st.columns(3)
col1.metric(label="Bronze (Crudos)", value=f"{total_bronze:,}")
col2.metric(label="Silver (Limpios)", value=f"{total_silver:,}")
col3.metric(label="Gold (Enriquecidos)", value=f"{total_gold:,}")

st.divider()

st.subheader("Demanda Laboral por Carrera Universitaria")

if not conteo_carreras.empty:
    fig = px.bar(
        conteo_carreras, 
        x='Cantidad de Ofertas', 
        y='Carrera', 
        orientation='h',
        text_auto=True,
        color='Cantidad de Ofertas',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos suficientes en la colección Gold para graficar las carreras.")
