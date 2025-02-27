import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Leer datos
df = pd.read_excel('inst.xlsx', index_col='#')

# Tratamiento de datos
dfroot = df[["CLAVES", "DESCRIPCIÓN", "PROVEEDOR", "PRECIO UNITARIO", "ABASTO", "MARCA"]]
df5 = df[["IMSS_25", "IMSS BIENESTAR_25", "ISSSTE_25", "SEMAR_25", "CENAPRECE_25", "CENSIDA_25", "CNEGSR_25", "CONASAMA_25", "PEMEX_25"]]
df6 = df[["IMSS_26", "IMSS BIENESTAR_26", "ISSSTE_26", "SEMAR_26", "CENAPRECE_26", "CENSIDA_26", "CNEGSR_26", "CONASAMA_26", "PEMEX_26"]]
bi = df5.add(df6.values, fill_value=0)
bi.columns = [col[:-1] + '5-26' for col in bi.columns]

# Variables
proveedores_unicos = df['PROVEEDOR'].unique()
claves_unicas = df['CLAVES'].unique()
medicamentos = [clave for clave in claves_unicas if int(clave.split('.')[0]) < 60]
material_curacion = [clave for clave in claves_unicas if int(clave.split('.')[0]) >= 60]
unico = df[df['ABASTO'] == 1]
simultaneo = df[df['ABASTO'] < 1]
ab_u = unico['CLAVES'].unique()
ab_s = simultaneo['CLAVES'].unique()

# Definimos funciones de Cálculo
def calcular_monto(data):
    data_monto = pd.DataFrame()
    for col in data.columns:
        data.loc[:, 'Monto ' + col] = data[col] * dfroot['PRECIO UNITARIO']
        data_monto = pd.concat([data_monto, data[['Monto ' + col]]], axis=1)
    return data_monto

def rooted(data):
    data_rooted = pd.concat([dfroot, data], axis=1)
    return data_rooted

# Definimos funciones para crear gráficos
def crear_pie(data):
    data['Tipo'] = data['CLAVES'].apply(lambda x: 'Medicamento' if int(x.split('.')[0]) < 60 else 'Material de Curación')
    return px.pie(data, names='Tipo', color='Tipo', color_discrete_map={'Medicamento': 'blue', 'Material de Curación': 'red'})

def crear_hist(data):
    data['Tipo'] = data['ABASTO'].apply(lambda x: 'Abastecimiento único' if x == 1 else 'Abastecimiento simultáneo')
    return px.histogram(data, x='Tipo', color='Tipo', color_discrete_map={'Abastecimiento único': 'green', 'Abastecimiento simultáneo': 'yellow'})

def visualMonto(data_inst, data):
    data_grouped = data.groupby("CLAVES").sum().reset_index()

    fig1 = px.line(data_grouped[data_grouped[data_inst] > 1000000], x="CLAVES", y=data_inst, title="CANTIDADES DEMANDADAS")
    fig2 = px.line(data_grouped[(data_grouped[data_inst] > 50000) & (data_grouped[data_inst] < 1000000)], x="CLAVES", y=data_inst)
    fig3 = px.line(data_grouped[(data_grouped[data_inst] > 1000) & (data_grouped[data_inst] < 50000)], x="CLAVES", y=data_inst)
    fig4 = px.line(data_grouped[(data_grouped[data_inst] > 0) & (data_grouped[data_inst] < 1000)], x="CLAVES", y=data_inst)
    
    fig1.show()
    fig2.show()
    fig3.show()
    fig4.show()

def visual(data_inst, data):
    data_grouped = data.groupby("CLAVES").sum().reset_index()

    fig1 = px.bar(data_grouped[data_grouped[data_inst] > 1000000], x="CLAVES", y=data_inst, title="CANTIDADES DEMANDADAS")
    fig2 = px.bar(data_grouped[(data_grouped[data_inst] > 50000) & (data_grouped[data_inst] < 1000000)], x="CLAVES", y=data_inst)
    fig3 = px.bar(data_grouped[(data_grouped[data_inst] > 1000) & (data_grouped[data_inst] < 50000)], x="CLAVES", y=data_inst)
    fig4 = px.bar(data_grouped[(data_grouped[data_inst] > 0) & (data_grouped[data_inst] < 1000)], x="CLAVES", y=data_inst)
    
    fig1.show()
    fig2.show()
    fig3.show()
    fig4.show()

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
    "General": claves_unicas,
    "Medicamento": medicamentos,
    "Material de Curación": material_curacion
}
birooted = rooted(bi)
rooted25 = rooted(df5)
rooted26 = rooted(df6)
# Pestañas
tab1, tab2 = st.tabs(["Adjudicación Directa", "Institutos"])

# Pestaña 1
with tab1:
    st.header("Resumen de Adjudicación Directa")

    selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="resumen_abasto")
    abastecimiento = abasto_options[selected_abasto]
    
    selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="resumen_type")
    ty = type_options[selected_type]
    
    clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="resumen_clave")
    cl = [clave_input] if clave_input != "TODAS LAS CLAVES" else claves_unicas
    
    # Filtrar datos
    datos_filtradosbi = birooted[(birooted['CLAVES'].isin(cl)) & (birooted['CLAVES'].isin(abastecimiento)) & (birooted['CLAVES'].isin(ty))]
    datos_filtrados25 = rooted25[(rooted25['CLAVES'].isin(cl)) & (rooted25['CLAVES'].isin(abastecimiento)) & (rooted25['CLAVES'].isin(ty))]
    datos_filtrados26 = rooted26[(rooted26['CLAVES'].isin(cl)) & (rooted26['CLAVES'].isin(abastecimiento)) & (rooted26['CLAVES'].isin(ty))]
    
    # Crear columnas
    col1, col2, col3 = st.columns(3)
    
    # Mostrar gráficos en columnas
    with col1:
        st.header("Tipo de Abastecimiento Bianual")
        st.plotly_chart(crear_pie(datos_filtradosbi), key="resumenbi_pie_oferta")
        st.header("Tipo de Clave Bianual")
        st.plotly_chart(crear_hist(datos_filtradosbi), key="resumenbi_hist_oferta")
    
    with col2:
        st.header("Tipo de Abastecimiento 2025")
        st.plotly_chart(crear_pie(datos_filtrados25), key="resumen25_pie_oferta")
        st.header("Tipo de Clave 2025")
        st.plotly_chart(crear_hist(datos_filtrados25), key="resumen25_hist_oferta")

    with col3:
        st.header("Tipo de Abastecimiento 2026")
        st.plotly_chart(crear_pie(datos_filtrados26), key="resumen26_pie_oferta")
        st.header("Tipo de Clave 2026")
        st.plotly_chart(crear_hist(datos_filtrados26), key="resumen26_hist_oferta")

# Pestaña 2
with tab2:
    st.header("CCINSHAE")

    selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="instituto_abasto")
    abastecimiento = abasto_options[selected_abasto]
    
    selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="instituto_type")
    ty = type_options[selected_type]
    
    clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="instituto_clave")
    cl = [clave_input] if clave_input != "TODAS LAS CLAVES" else claves_unicas
    
    # Filtrar datos
    datos_filtrados = df[(df['CLAVES'].isin(cl)) & (df['CLAVES'].isin(abastecimiento)) & (df['CLAVES'].isin(ty))]
    
    # Crear columnas
    col1, col2 = st.columns(2)
    
    # Mostrar gráficos en columnas
    with col1:
        st.header("Tipo de Abastecimiento")
        st.plotly_chart(crear_pie(datos_filtrados), key="instituto_pie_oferta")
        
    
    with col2:
        st.header("Tipo de Clave")
        st.plotly_chart(crear_hist(datos_filtrados), key="instituto_hist_oferta")

# Incluir imagen como pie de página
st.image("footer.png", use_container_width=True)
