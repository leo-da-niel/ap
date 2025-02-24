import streamlit as st
import pandas as pd
import plotly.express as px

# Título del dashboard
st.title("Dashboard básico con Streamlit")

# Cargar datos
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv")

# Selector de año
year = st.slider("Selecciona un año", int(df['year'].min()), int(df['year'].max()))

# Filtrar datos por año
filtered_df = df[df['year'] == year]

# Gráfico de dispersión interactivo
fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp", size="pop", color="continent", hover_name="country")
st.plotly_chart(fig)
