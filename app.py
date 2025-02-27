import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Leer datos
df = pd.read_excel('inst.xlsx', index_col='#')

# Variables
proveedores_unicos = df['PROVEEDOR'].unique()
claves_unicas = df['CLAVES'].unique()
#medicamentos = [clave for clave in claves_unicas if int(clave.split('.')[0]) < 60]
#material_curacion = [clave for clave in claves_unicas if int(clave.split('.')[0]) >= 60]
unico = df[df['ABASTO'] == 1]
simultaneo = df[df['ABASTO'] < 1]
ab_u = unico['CLAVES'].unique()
ab_s = simultaneo['CLAVES'].unique()

# Definir funciones para crear gráficos
def crear_pie(data):
    data['Tipo'] = data['CLAVES'].apply(lambda x: 'Medicamento' if int(x.split('.')[0]) < 60 else 'Material de Curación')
    return px.pie(data, names='Tipo', color='Tipo', color_discrete_map={'Medicamento': 'blue', 'Material de Curación': 'red'})

# Configuración de la página
st.set_page_config(page_title="Dashboard", layout="wide")

# Incluir imagen como encabezado
st.image("header.png", use_container_width=True)

# Opciones
clave_options = {"TODAS LAS CLAVES": "General", **{clave: clave for clave in claves_unicas}}

instituto_options = {
    "IMSS": "IMSS",
    "IMSS BIENESTAR": "IMSS BIENESTAR",
    "ISSSTE": "ISSSTE",
    "SEMAR": "SEMAR",
    "CENAPRECE": "CENAPRECE",
    "CENISDA": "CENISDA",
    "CNEGRS": "CNEGRS",
    "CONASAMA": "CONASAMA",
    "PEMEX": "PEMEX"
}
proveedor_options = {proveedor: proveedor for proveedor in proveedores_unicos}

abasto_options = {
    "General": claves_unicas,
    "Abastecimiento simultáneo": ab_s,
    "Abastecimiento único": ab_u
}

type_options = {
    "General": "General",
    claves_unicas,
    "Medicamento": "Medicamento",
    medicamentos,
    "Material de Curación": "Material de Curación"
    material_curacion
}

selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="resumen_abasto")
abastecimiento = abasto_options[selected_abasto]

selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="resumen_type")
ty = type_options[selected_type]

clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="resumen_clave")
cl = [clave_input] if clave_input != "TODAS LAS CLAVES" else claves_unicas

# Filtrar datos
datos_filtrados = df[(df['CLAVES'].isin(cl)) & (df['CLAVES'].isin(abastecimiento)) & (df['CLAVES'].isin(ty))]

# Mostrar gráficos 
st.plotly_chart(crear_pie(datos_filtrados), key="resumen_pie_oferta")

# Incluir imagen como pie de página
st.image("footer.png", use_container_width=True)
