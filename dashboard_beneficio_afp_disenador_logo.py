
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Simulador AFP", layout="wide", page_icon="💼")

# Cabecera con logo
st.markdown(
    """
    <div style='display:flex;align-items:center;justify-content:space-between;background-color:#003366;padding:20px 30px;border-radius:10px;margin-bottom:20px'>
        <img src='https://raw.githubusercontent.com/rfuentesnz/dashboard-afp/main/logo_afp.png' width='150'>
        <div style='text-align:right'>
            <h1 style='color:white;margin-bottom:5px;'>Simulador de Beneficio AFP</h1>
            <h4 style='color:#cfe2ff;'>IA + Visualización Interactiva</h4>
        </div>
    </div>
    """, unsafe_allow_html=True
)

@st.cache_data
def cargar_datos():
    df = pd.read_csv("resumen_beneficio_afp.csv", sep=None, engine='python')
    df.columns = df.columns.str.lower().str.strip()
    df['sexo'] = df['sexo'].str.upper().str.strip()
    return df

df = cargar_datos()
if df.empty:
    st.stop()

st.sidebar.header("🎛️ Filtros Interactivos")
sexo = st.sidebar.selectbox("Sexo", options=["Todos", "F", "M"])
edad_min = st.sidebar.slider("Edad mínima", 18, 90, 65)
edad_max = st.sidebar.slider("Edad máxima", 18, 90, 90)
meses_min = st.sidebar.slider("Meses cotizados mínimos", 0, 500, 0)
solo_pensionados = st.sidebar.checkbox("Solo pensionados", value=True)

filtro = (df['edad'] >= edad_min) & (df['edad'] <= edad_max)
filtro &= (df['meses_cotizados'] >= meses_min)
if sexo != "Todos":
    filtro &= (df['sexo'] == sexo)
if solo_pensionados:
    filtro &= (df['pensionado'] == 1)

df_filtrado = df[filtro]

st.markdown("## 📊 Estadísticas Principales")
col1, col2, col3 = st.columns(3)
col1.metric("🔢 Personas Filtradas", len(df_filtrado))
col2.metric("✅ Reciben Beneficio", int(df_filtrado['consultara_beneficio'].sum()))
col3.metric("❌ No Reciben", int(len(df_filtrado) - df_filtrado['consultara_beneficio'].sum()))

st.divider()

st.markdown("## 🧠 Visualización Interactiva")
tab1, tab2, tab3 = st.tabs(["Beneficio", "Distribución", "Edad vs Cotización"])

with tab1:
    fig1 = px.pie(df_filtrado, names='consultara_beneficio',
                  title="Distribución de Beneficio", color_discrete_sequence=['salmon', 'seagreen'],
                  labels={0: "No Reciben", 1: "Reciben"})
    fig1.update_traces(textinfo='percent+label')
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.histogram(df_filtrado, x='edad', nbins=20, color='consultara_beneficio',
                        title="Distribución de Edad", barmode='overlay', color_discrete_sequence=['#FF9999', '#66CC99'])
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.histogram(df_filtrado, x='meses_cotizados', nbins=30,
                        title="Distribución de Meses Cotizados", color='consultara_beneficio',
                        color_discrete_sequence=['#FF9999', '#66CC99'])
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    fig4 = px.scatter(df_filtrado, x='edad', y='meses_cotizados',
                      color='consultara_beneficio', size='ingresos', hover_data=['sexo'],
                      title="Relación Edad vs. Cotización",
                      color_discrete_sequence=['#FF6666', '#00CC99'],
                      labels={'consultara_beneficio': 'Beneficio'})
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.markdown("## 📄 Detalle de Datos Filtrados")

st.download_button(
    label="📥 Descargar Excel",
    data=df_filtrado.to_csv(index=False).encode('utf-8'),
    file_name="beneficiarios_filtrados.csv",
    mime='text/csv'
)

st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)
