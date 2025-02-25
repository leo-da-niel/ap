import streamlit as st
import pandas as pd
import plotly.express as px  # Importar plotly para los gráficos interactivos

# Leer datos
oferta = pd.read_csv("dash.csv", encoding='latin-1', index_col='propuesta')
demanda = pd.read_csv("board.csv", encoding='latin-1', index_col='partida')

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

st.sidebar.title("Ingrese la Clave, Instituto o Proveedor")
# Entrada de símbolos y pesos
clave_options = {
    "a": "a",
    "b": "b",
    "c": "c",
    "d": "d"
}
clave_input = st.sidebar.selectbox("Ingrese la clave o claves separadas por coma", list(clave_options.keys()))
cl = [s.strip() for s in clave_input.split(',')]

instituto_options = {
    "imss": "imss",
    "imssbienestar": "imssbienestar",
    "issste": "issste",
    "pemex": "pemex"
}
selected_instituto = st.sidebar.selectbox("Ingrese el Instituto:", list(instituto_options.keys()))
inst = instituto_options[selected_instituto]

proveedor_options = {
    "w": "w",
    "x": "x",
    "y": "y",
    "z": "z"
}
selected_proveedor = st.sidebar.selectbox("Ingrese el proveedor", list(proveedor_options.keys()))
prov = proveedor_options[selected_proveedor]

status_options = {
    "Desiertas": "desierta",
    "Adjudicación Única": "único",
    "Abastecimiento Simultáneo": "simultáneo",
    "Sin Oferta": "sin oferta"
}
selected_status = st.sidebar.selectbox("Ingrese el estatus", list(status_options.keys()))
stat = status_options[selected_status]

type_options = {
    "Medicamento": "Medicamento",
    "Material de Curación": "Material de Curación"
}
selected_type = st.sidebar.selectbox("Ingrese el tipo de clave", list(type_options.keys()))
ty = type_options[selected_type]

# Pestañas
tab1, tab2, tab3 = st.tabs(["Resumen de licitación", "Oferta", "Demanda"])

# Pestaña 1: Resumen de licitación
with tab1:
    st.header("Resumen de licitación")

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

    # Crear un DataFrame con la información
    resumen_data = {
        "Métrica": ["TOTAL DE PROPUESTAS", "OFERTAS PARA ANÁLISIS", "ADJUDICADAS", "DESIERTAS", "PROPUESTAS EFECTIVAS", "SIN OFERTA%", "SIMULTÁNEAS"],
        "Valor": [prop, of, adj, des, efect, so, absim]
    }
    resumen_df = pd.DataFrame(resumen_data)
    st.dataframe(resumen_df.style.format({"Valor": "{:.0f}"}))

    # Mostrar gráficos 
    st.plotly_chart(fig_histogram_oferta, key="resumen_histogram_oferta")
    st.plotly_chart(fig_pie_oferta, key="resumen_pie_oferta")
    st.plotly_chart(fig_histogram_demanda, key="resumen_histogram_demanda")
    st.plotly_chart(fig_pie_demanda, key="resumen_pie_demanda") 
    st.plotly_chart(fig_hist_of_ad, key="resumen_hist_of_ad")

# Pestaña 2: Oferta
with tab2:
    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL DE PROPUESTAS", f"{prop}")
    col2.metric("OFERTAS PARA ANÁLISIS", f"{of}")
    col3.metric("PROPUESTAS EFECTIVAS", f"{efect}")
    
    st.header("Oferta")
    st.write(oferta.head())
    
    # Mostrar gráficos interactivos
    st.plotly_chart(fig_histogram_oferta, key="oferta_histogram")
    st.plotly_chart(fig_pie_oferta, key="oferta_pie")
    st.plotly_chart(fig_hist_of_ad, key="oferta_hist_of_ad")

# Pestaña 3: Demanda
with tab3:
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
