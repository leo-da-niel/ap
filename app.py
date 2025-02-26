import streamlit as st
import pandas as pd
import plotly.express as px  # Importar plotly para los gráficos interactivos

# Leer datos
oferta = pd.read_csv("dash.csv", encoding='latin-1', index_col='propuesta')
demanda = pd.read_csv("board.csv", encoding='latin-1', index_col='partida')
#df = pd.read_excel('inst.xlsx', index_col = '#')

# Variables
prop = oferta['clave'].nunique()
of = len(oferta[oferta['estatus'] != 'no procedente'])
efect = len(oferta[oferta['estatus'] != 'no procedente'])

adj = len(demanda[demanda['estatus'].isin(['único', 'simultáneo'])])
des = len(demanda[demanda['estatus'] == 'desierta'])
so = len(demanda[demanda['estatus'] == 'sin oferta'])
absim = len(demanda[demanda['estatus'] == 'simultáneo'])

# Crear gráficos con Plotly
fig_histogram_oferta = px.histogram(oferta, x="proveedor", title="Distribución de Adjudicación por Proveedor")
fig_pie_oferta = px.pie(oferta, names='estatus', title='Distribución de Estatus de Oferta')
fig_hist_of_ad = px.histogram(oferta, x='adjudicación (%)', title='Distribución de Adjudicación (%)')

fig_histogram_demanda = px.histogram(demanda, x="proveedores", title="Distribución de Proveedores")
fig_pie_demanda = px.pie(demanda, names='estatus', title='Distribución de Estatus de Demanda')

# Configuración de la página
st.set_page_config(page_title="Dashboard", layout="wide")

# Incluir imagen como encabezado
st.image("header.png", use_container_width=True)

# Opciones
clave_options = {
    "a": "a",
    "b": "b",
    "c": "c",
    "d": "d"
}

instituto_options = {
    "imss": "imss",
    "imssbienestar": "imssbienestar",
    "issste": "issste",
    "pemex": "pemex"
}

proveedor_options = {
    "w": "w",
    "x": "x",
    "y": "y",
    "z": "z"
}

status_options = {
    "Desiertas": "desierta",
    "Adjudicación Única": "único",
    "Abastecimiento Simultáneo": "simultáneo",
    "Sin Oferta": "sin oferta"
}

type_options = {
    "Medicamento": "Medicamento",
    "Material de Curación": "Material de Curación"
}

# Pestañas
tab1, tab2, tab3 = st.tabs(["Resumen de licitación", "Oferta", "Demanda"])

# Pestaña 1: Resumen de licitación
with tab1:
    selected_status = st.selectbox("Ingrese el estatus", list(status_options.keys()), key="resumen_status")
    stat = status_options[selected_status]

    selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="resumen_type")
    ty = type_options[selected_type]

    # Crear un contenedor para el recuadro
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("TOTAL DE PROPUESTAS", f"{prop}")
        col2.metric("OFERTAS PARA ANÁLISIS", f"{of}")
        col3.metric("ADJUDICADAS", f"{adj}")
        col4.metric("DESIERTAS", f"{des}")
        
        col5, col6, col7 = st.columns(3)
        col5.metric("PROPUESTAS EFECTIVAS", f"{efect}")
        col6.metric("SIN OFERTA%", f"{so}")
        col7.metric("SIMULTÁNEAS", f"{absim}")

    clave_input = st.selectbox("Ingrese la clave o claves separadas por coma", list(clave_options.keys()), key="resumen_clave")
    cl = [s.strip() for s in clave_input.split(',')]

    # Mostrar gráficos 
    st.plotly_chart(fig_histogram_oferta, key="resumen_histogram_oferta")
    st.plotly_chart(fig_pie_oferta, key="resumen_pie_oferta")
    st.plotly_chart(fig_histogram_demanda, key="resumen_histogram_demanda")
    st.plotly_chart(fig_pie_demanda, key="resumen_pie_demanda") 
    st.plotly_chart(fig_hist_of_ad, key="resumen_hist_of_ad")

# Pestaña 2: Oferta
with tab2:
    clave_input = st.selectbox("Ingrese la clave o claves separadas por coma", list(clave_options.keys()), key="oferta_clave")
    cl = [s.strip() for s in clave_input.split(',')]

    selected_proveedor = st.selectbox("Ingrese el proveedor", list(proveedor_options.keys()), key="oferta_proveedor")
    prov = proveedor_options[selected_proveedor]

    selected_status = st.selectbox("Ingrese el estatus", list(status_options.keys()), key="oferta_status")
    stat = status_options[selected_status]

    # Mostrar gráficos específicos de la oferta
    st.plotly_chart(fig_histogram_oferta, key="oferta_histogram_oferta")
    st.plotly_chart(fig_pie_oferta, key="oferta_pie_oferta")

# Pestaña 3: Demanda
with tab3:
    selected_instituto = st.selectbox("Ingrese el Instituto:", list(instituto_options.keys()), key="demanda_instituto")
    inst = instituto_options[selected_instituto]

    clave_input = st.selectbox("Ingrese la clave o claves separadas por coma", list(clave_options.keys()), key="demanda_clave")
    cl = [s.strip() for s in clave_input.split(',')]

    selected_status = st.selectbox("Ingrese el estatus", list(status_options.keys()), key="demanda_status")
    stat = status_options[selected_status]

    selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="demanda_type")
    ty = type_options[selected_type]

    # Mostrar gráficos específicos de la demanda
    st.plotly_chart(fig_histogram_demanda, key="demanda_histogram_demanda")
    st.plotly_chart(fig_pie_demanda, key="demanda_pie_demanda")

    col4, col5, col6, col7 = st.columns(4)
    col4.metric("ADJUDICADAS", f"{adj}")
    col5.metric("SIN OFERTA%", f"{so}")
    col6.metric("DESIERTAS", f"{des}")
    col7.metric("SIMULTÁNEAS", f"{absim}")

    # Mostrar gráficos interactivos
    st.plotly_chart(fig_histogram_demanda, key="demanda_histogram")
    st.plotly_chart(fig_pie_demanda, key="demanda_pie")

    st.header("Demanda")
    st.write(demanda.head())

# Incluir imagen como pie de página
st.image("footer.png", use_container_width=True)
