import streamlit as st
import pandas as pd
import plotly.express as px

# Título del dashboard
st.title("Dashboard con múltiples visualizaciones")

# Cargar datos
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/tips.csv")

# Gráfico de barras
st.header("Gráfico de barras")
fig1 = px.bar(df, x="day", y="total_bill", color="sex", barmode="group")
st.plotly_chart(fig1)

# Gráfico de líneas
st.header("Gráfico de líneas")
fig2 = px.line(df, x="day", y="total_bill", color="sex")
st.plotly_chart(fig2)

# Histograma
st.header("Histograma")
fig3 = px.histogram(df, x="total_bill", color="sex")
st.plotly_chart(fig3)
