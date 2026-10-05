# (Capa de Presentación - SRP)
# Es el punto de entrada de Streamlit. Solo se encarga de dibujar la interfaz, utilizando el caché de Streamlit para no golpear la base de datos en cada clic.
import streamlit as st
import plotly.express as px
from database import get_database
from data_processing import get_general_metrics, get_source_distribution, get_careers_distribution, generate_analytical_insights, get_geographic_distribution


st.set_page_config(page_title="Ofertas Laborales", layout="wide", initial_sidebar_state="collapsed")

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
    # Nuevos datos geográficos
    total_silver, df_pais, resumen_cat, df_provincia, df_ciudad = get_geographic_distribution(db)
    # return t_bronze, t_gold, survival_rate, df_sources, df_careers, insights
    return t_bronze, t_gold, survival_rate, df_sources, df_careers, insights, total_silver, df_pais, resumen_cat, df_provincia, df_ciudad


# t_bronze, t_gold, survival_rate, df_sources, df_careers, insights = load_dashboard_data()
t_bronze, t_gold, survival_rate, df_sources, df_careers, insights, total_silver, df_pais, resumen_cat, df_provincia, df_ciudad = load_dashboard_data()


# --- Estilos Globales para Gráficos Plotly ---
PLOTLY_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#334155"), 
    margin=dict(l=0, r=0, t=40, b=0)
)

# --- Interfaz Visual ---
st.title("Proyecto: Ofertas Laborales")
st.markdown("### Análisis de Impacto y Relevancia del Mercado Laboral")
st.markdown("Desarrollado por: **Ozzy Loachamín**")
st.divider()

# Crear sistema de pestañas
tab1, tab2 = st.tabs(["Visión General y Carreras", "Distribución Geográfica"])

with tab1:
    st.markdown("### Análisis de Impacto y Relevancia del Mercado Laboral")

    # 1. KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Volumen Total Extraído", value=f"{t_bronze:,}")
    col2.metric(label="Ofertas Viables (Filtradas)", value=f"{t_gold:,}")
    col3.metric(
        label="Tasa de Utilidad Global", 
        value=f"{survival_rate:.1f}%",
        delta="Retención después del NLP",
        delta_color="normal"
    )

    st.divider()

    # 2. Análisis de Embudos y Fuentes
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Reducción de Ruido: Extracción vs. Viabilidad")
        data_funnel = dict(
            # Aquí también corregimos los nombres
            number=[t_bronze, t_gold],
            stage=["Universo Crudo", "Perfil EPN"]
        )
        fig_funnel = px.funnel(data_funnel, x='number', y='stage')
        
        # Personalización del embudo (colores, tooltip limpio y sin eje Y redundante)
        fig_funnel.update_traces(
            marker={"color": ["#cbd5e1", "#0369a1"]},
            hovertemplate="<b>%{y}</b><br>Total: %{x} ofertas<extra></extra>",
            textfont=dict(size=14, color="white") # Eliminado weight="bold"
        )
        fig_funnel.update_yaxes(title_text="")
        fig_funnel.update_layout(**PLOTLY_THEME)
        
        # El config oculta la barra de herramientas molesta de Plotly
        st.plotly_chart(fig_funnel, use_container_width=True, config={'displayModeBar': False})

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
                    "2. Después (Ofertas Útiles)": "#0369a1"
                }
            )
            # Etiquetas horizontales y reubicación de leyenda
            fig_sources.update_traces(
                textangle=0, 
                textposition="outside"
                # Eliminado textfont=dict(weight="bold")
            )
            fig_sources.update_layout(
                **PLOTLY_THEME,
                legend=dict(
                    title_text='', 
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="center", 
                    x=0.5
                ),
                xaxis_title="", 
                yaxis_title="", 
                yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False)
            )
            st.plotly_chart(fig_sources, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    # 3. Gráfico de Carreras
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
            
            fig_careers.update_traces(
                marker_color="#0369a1", 
                textangle=0, 
                textposition="outside",
                textfont=dict(color="#334155") # Eliminado weight="bold"
            )
            
            fig_careers.update_layout(
                **PLOTLY_THEME, 
                yaxis={'categoryorder':'total ascending', 'title_text': 'Carrera'}, 
                xaxis={'visible': True, 'title_text': 'Cantidad de Ofertas'}, # Oculta el eje X inferior (ya tenemos los números en las barras)
                height=700
            )
            st.plotly_chart(fig_careers, use_container_width=True, config={'displayModeBar': False})

    with col_text:
        st.markdown("#### Conclusiones Automáticas")
        if insights:
            for insight in insights:
                st.info(insight, icon="💡")
        else:
            st.write("Datos insuficientes para generar conclusiones automáticas.")

with tab2:
    st.markdown("### Cobertura Territorial de Ofertas Laborales (Capa Silver)")
    
    # --- NUEVO CALLOUT INFORMATIVO ---
    st.info(
        "**Nota:** Los datos geográficos presentados a continuación reflejan el "
        "universo total de ofertas normalizadas. No se restringen a los perfiles y carreras de la EPN "
        "(cuyo filtrado ocurre en la Capa Gold), sino que abarcan todas las áreas de conocimiento "
        "disponibles en los portales extraídos: Computrabajo, Get on Board, Multitrabajos y Talent.",
        icon="ℹ️"
    )
    # ---------------------------------

    # 1. KPIs Geográficos
    col_geo1, col_geo2 = st.columns(2)
    col_geo1.metric(label="Total Ofertas en Base Base (Silver)", value=f"{total_silver:,}")
    ofertas_ec = resumen_cat.loc[resumen_cat['Categoría'] == 'Ecuador', 'Ofertas'].values[0] if not resumen_cat.empty else 0
    col_geo2.metric(label="Ofertas Nacionales (Ecuador)", value=f"{ofertas_ec:,}")
    
    st.divider()

    # 2. Gráfico Nacional vs Internacional
    col_map1, col_map2 = st.columns([1, 2])
    
    with col_map1:
        st.subheader("Alcance")
        if not resumen_cat.empty:
            fig_cat = px.pie(
                resumen_cat, 
                values='Ofertas', 
                names='Categoría', 
                hole=0.4,
                color_discrete_sequence=["#0284c7", "#94a3b8"]
            )
            fig_cat.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig_cat, use_container_width=True)

    with col_map2:
        st.subheader("Top Países Internacionales")
        if not df_pais.empty:
            # Filtramos solo los internacionales para este gráfico
            df_internacional = df_pais[df_pais['Categoría'] == 'Internacional'].head(10)
            if not df_internacional.empty:
                fig_paises = px.bar(
                    df_internacional, 
                    x='Ofertas', 
                    y='País', 
                    orientation='h', 
                    text_auto=True
                )
                fig_paises.update_traces(marker_color="#475569", textangle=0, textposition="outside")
                fig_paises.update_layout(**PLOTLY_THEME, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_paises, use_container_width=True)
            else:
                st.info("No se registran ofertas fuera de Ecuador.")

    st.divider()

    st.markdown('<div style="page-break-before: always;"></div>', unsafe_allow_html=True)

    # 3. Gráficos Provinciales y Locales
    col_prov, col_ciu = st.columns(2)
    
    with col_prov:
        st.subheader("Distribución por Provincia (EC)")
        if not df_provincia.empty:
            fig_prov = px.bar(
                df_provincia, 
                x='Ofertas', 
                y='Provincia', 
                orientation='h',
                text_auto=True
            )
            fig_prov.update_traces(marker_color="#0369a1", textangle=0, textposition="outside")
            fig_prov.update_layout(**PLOTLY_THEME, yaxis={'categoryorder':'total ascending'}, height=500)
            st.plotly_chart(fig_prov, use_container_width=True)

    with col_ciu:
        st.subheader("Top 15 Ciudades (EC)")
        if not df_ciudad.empty:
            fig_ciu = px.bar(
                df_ciudad, 
                x='Ofertas', 
                y='Ciudad', 
                orientation='h',
                text_auto=True
            )
            fig_ciu.update_traces(marker_color="#0ea5e9", textangle=0, textposition="outside")
            fig_ciu.update_layout(**PLOTLY_THEME, yaxis={'categoryorder':'total ascending'}, height=500)
            st.plotly_chart(fig_ciu, use_container_width=True)