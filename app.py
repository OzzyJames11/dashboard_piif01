# (Capa de Presentación - SRP)
# Es el punto de entrada de Streamlit. Solo se encarga de dibujar la interfaz, utilizando el caché de Streamlit para no golpear la base de datos en cada clic.
import streamlit as st
import plotly.express as px
from database import get_database
from data_processing import get_general_metrics, get_source_distribution, get_careers_distribution, generate_analytical_insights

st.set_page_config(page_title="Observatorio Laboral EPN", layout="wide", initial_sidebar_state="collapsed")

# --- Estilos Globales para Gráficos Plotly ---
PLOTLY_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif"),
    margin=dict(l=0, r=0, t=40, b=0)
)

# --- Caché y Carga de Datos ---
@st.cache_resource
def init_db():
    return get_database()

@st.cache_data(ttl=3600)
def load_dashboard_data():
    db = init_db()
    t_bronze, t_gold, survival_rate = get_general_metrics(db)
    df_sources = get_source_distribution(db)
    df_careers = get_careers_distribution(db)
    insights = generate_analytical_insights(df_sources, t_bronze, t_gold)
    return t_bronze, t_gold, survival_rate, df_sources, df_careers, insights

t_bronze, t_gold, survival_rate, df_sources, df_careers, insights = load_dashboard_data()

# --- Interfaz Visual ---
st.title("Proyecto: Ofertas Laborales")
st.markdown("### Análisis de Impacto y Relevancia del Mercado Laboral")
st.markdown("Desarrollado por: Ozzy Loachamín")
st.divider()

# 1. KPIs
col1, col2, col3 = st.columns(3)
col1.metric(label="Volumen Total Extraído", value=f"{t_bronze:,}")
col2.metric(label="Ofertas Viables (Filtradas)", value=f"{t_gold:,}")
col3.metric(
    label="Tasa de Utilidad Global", 
    value=f"{survival_rate:.1f}%",
    delta="Retención tras NLP",
    delta_color="normal"
)

st.divider()

# 2. Análisis de Embudos y Fuentes
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Reducción de Ruido: Extracción vs. Viabilidad")
    data_funnel = dict(
        number=[t_bronze, t_gold],
        stage=["Universo Crudo", "Perfil EPN"]
    )
    fig_funnel = px.funnel(data_funnel, x='number', y='stage')
    fig_funnel.update_traces(marker={"color": ["#94a3b8", "#0284c7"]})
    fig_funnel.update_layout(**PLOTLY_THEME)
    st.plotly_chart(fig_funnel, use_container_width=True, theme="streamlit")

with col_chart2:
    st.subheader("Rendimiento de Fuentes: Volumen vs. Relevancia")
    if not df_sources.empty:
        fig_sources = px.bar(
            df_sources, 
            x='Fuente', 
            y='Cantidad', 
            color='Etapa',
            barmode='group',
            text_auto=True,
            color_discrete_map={
                "1. Antes (Universo Scrapeado)": "#cbd5e1",
                "2. Después (Ofertas Útiles)": "#0284c7"
            }
        )
        fig_sources.update_traces(textangle=0, textposition="outside")
        fig_sources.update_layout(**PLOTLY_THEME, legend_title_text='')
        st.plotly_chart(fig_sources, use_container_width=True, theme="streamlit")

st.divider()

# 3. Gráfico de Carreras con color sólido
st.subheader("Distribución de Oportunidades por Carrera")

col_bar, col_text = st.columns([7, 3])

with col_bar:
    if not df_careers.empty:
        fig_careers = px.bar(
            df_careers, 
            x='Cantidad de Ofertas', 
            y='Carrera', 
            orientation='h',
            text_auto=True
        )
        # Se elimina la escala continua y se fija un color sólido elegante para alto contraste
        fig_careers.update_traces(marker_color="#0369a1", textangle=0, textposition="outside")
        # fig_careers.update_traces(marker_color="#0369a1")
        fig_careers.update_layout(**PLOTLY_THEME, yaxis={'categoryorder':'total ascending'}, height=650)
        st.plotly_chart(fig_careers, use_container_width=True, theme="streamlit")

with col_text:
    st.markdown("#### Conclusiones Extraídas")
    if insights:
        for insight in insights:
            st.info(insight, icon="💡")
    else:
        st.write("Datos insuficientes para generar conclusiones automáticas.")
        
    # st.markdown("#### Recomendaciones Analíticas")
    # st.markdown("""
    # * **Optimización de Scraping:** Considerar reducir la frecuencia de extracción en plataformas de alto volumen y baja conversión (ruido) para ahorrar recursos de cómputo en el servidor Páramo.
    # * **Focalización:** Priorizar la integración de nuevas plataformas de nicho tecnológico (similares a Get On Board), ya que su arquitectura de datos alinea mejor con las ingenierías.
    # """)