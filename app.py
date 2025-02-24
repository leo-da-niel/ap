import streamlit as st
import pandas as pd
import plotly.express as px

# Título del dashboard
st.title("Mapa interactivo con Streamlit")

# Cargar datos geoespaciales
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv")

# Crear mapa
fig = px.choropleth(df, locations="CODE", color="GDP (BILLIONS)", hover_name="COUNTRY", projection="natural earth")
st.plotly_chart(fig)
