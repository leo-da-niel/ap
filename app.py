import streamlit as st
import pandas as pd
import plotly.express as px

# Título del dashboard
st.title("Dashboard con carga de archivos")

# Cargar archivo CSV
uploaded_file = st.file_uploader("Sube un archivo CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Vista previa de los datos:")
    st.write(df.head())

    # Gráfico de dispersión
    st.header("Gráfico de dispersión")
    fig = px.scatter(df, x=df.columns[0], y=df.columns[1])
    st.plotly_chart(fig)
