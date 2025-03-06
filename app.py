import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
import altair as alt

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
nproveedores_unicos = df['PROVEEDOR'].nunique()
nclaves_unicas = df['CLAVES'].nunique()
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
        data.loc[:, 'MONTO ' + col] = data[col] * dfroot['PRECIO UNITARIO']
        data_monto = pd.concat([data_monto, data[['MONTO ' + col]]], axis=1)
    return data_monto

def rooted(data):
    data_rooted = pd.concat([dfroot, data], axis=1)
    return data_rooted
    
def totales(data):
    data_total = data.sum(axis=1)
    data_total_df = pd.DataFrame(data_total, columns=['TOTAL'])
    return data_total_df

def grouping(data):
    data_grouped= data.groupby("CLAVES").sum().reset_index()
    return data_grouped

def filtrar_inst(nombre_inst):
    data_inst = pd.DataFrame()
    nombre_inst25 = nombre_inst + "_25"
    nombre_inst26 = nombre_inst + "_26"
    nombre_instbi = nombre_inst + "_25-26"
    data_inst = pd.concat([data_inst, df[[nombre_inst25, nombre_inst26]]], axis=1)
    data_inst = pd.concat([data_inst, bi[[nombre_instbi]]], axis=1)
    return data_inst

def nonz(data):
    datanz = data[data.iloc[:,-1] !=0]
    return datanz


# Definimos funciones para crear gráficos
def crear_pie(data):
    data['Tipo'] = data['CLAVES'].apply(lambda x: 'Medicamento' if int(x.split('.')[0]) < 60 else 'Material de Curación')
    return px.pie(data, names='Tipo', color='Tipo', color_discrete_map={'Medicamento': 'blue', 'Material de Curación': 'red'}, width=400, height=400)

def crear_hist(data):
    data['Tipo'] = data['ABASTO'].apply(lambda x: 'Abastecimiento único' if x == 1 else 'Abastecimiento simultáneo')
    return px.histogram(data, x='Tipo', color='Tipo', color_discrete_map={'Abastecimiento único': 'green', 'Abastecimiento simultáneo': 'yellow'}, width=400, height=400)

def visualMonto(data_inst, data):
    data_grouped = data.groupby("CLAVES").sum().reset_index()

    fig1 = px.line(data_grouped[data_grouped[data_inst] > 1000000], x="CLAVES", y=data_inst, title="Importe ($)", markers=True)
    fig2 = px.line(data_grouped[(data_grouped[data_inst] > 50000) & (data_grouped[data_inst] < 1000000)], x="CLAVES", y=data_inst, markers=True)
    fig3 = px.line(data_grouped[(data_grouped[data_inst] > 1000) & (data_grouped[data_inst] < 50000)], x="CLAVES", y=data_inst, markers=True)
    fig4 = px.line(data_grouped[(data_grouped[data_inst] > 0) & (data_grouped[data_inst] < 1000)], x="CLAVES", y=data_inst, markers=True)
    return [fig1, fig2, fig3, fig4]

def visual(data_inst, data):
    data_grouped = data.groupby("CLAVES").sum().reset_index()

    fig5 = px.bar(data_grouped[data_grouped[data_inst] > 1000000], x="CLAVES", y=data_inst, title="CANTIDADES")
    fig6 = px.bar(data_grouped[(data_grouped[data_inst] > 50000) & (data_grouped[data_inst] < 1000000)], x="CLAVES", y=data_inst)
    fig7 = px.bar(data_grouped[(data_grouped[data_inst] > 1000) & (data_grouped[data_inst] < 50000)], x="CLAVES", y=data_inst)
    fig8 = px.bar(data_grouped[(data_grouped[data_inst] > 0) & (data_grouped[data_inst] < 1000)], x="CLAVES", y=data_inst) 
    return [fig5, fig6, fig7, fig8]
def Vvisual(data_inst, data):
    data_grouped = data.groupby("CLAVES").sum().reset_index()
    data_top10 = data_grouped.nlargest(10, data_inst)
    fig = px.bar(data_top10, x="CLAVES", y=data_inst, title="TOP 10 CANTIDADES DEMANDADAS")
    #fic = fig.update_traces(mode='markers+lines+text', text=data_top10[data_inst], textposition="top center")
    return fig
    #fig.show()
    
def VvisualMonto(data_inst, data):
    data_grouped = data.groupby("CLAVES").sum().reset_index()
    data_top10 = data_grouped.nlargest(10, data_inst)
    fig = px.line(data_top10, x="CLAVES", y=data_inst, title="TOP 10 IMPORTE ($) POR CLAVE", markers=True)
    fig.add_trace(go.Scatter(
        x=data_top10["CLAVES"],
        y=data_top10[data_inst],
        mode='text',
        text=data_top10[data_inst].astype(str),
        textposition="top center"
    ))
    #fic = fig.update_traces(mode='markers+lines+text', text=data_top10[data_inst], textposition="top center")
    return fig
    #return fic

warnings.filterwarnings("ignore", category=FutureWarning, module="altair")
def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    elif input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    elif input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    elif input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "value": [100, 0]
    })
    
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response}%'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text

# Configuración de la página
st.set_page_config(page_title="Dashboard", layout="wide")

# Incluir imagen como encabezado
st.image("header.png", use_container_width=True)

# Opciones
clave_options = {"TODAS LAS CLAVES": "General", **{clave: clave for clave in claves_unicas}}

periodo_options = {
"BIANUAL": "BIANUAL",
"2025": "2025",
"2026": "2026"
}
    
instituto_options = {
    "IMSS": "IMSS",
    "IMSS BIENESTAR": "IMSS BIENESTAR",
    "ISSSTE": "ISSSTE",
    "SEMAR": "SEMAR",
    "CENAPRECE": "CENAPRECE",
    "CENSIDA": "CENSIDA",
    "CNEGSR": "CNEGSR",
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

df25 = pd.concat([df5, totales(df5)], axis=1)
df26 = pd.concat([df6, totales(df6)], axis=1)
bit  = pd.concat([bi, totales(bi)], axis=1)

bitrooted = rooted(bit)
rooted25 = rooted(df25)
rooted26 = rooted(df26)

nzbitrooted = bitrooted[bitrooted["TOTAL"] !=0]
nzrooted25 = rooted25[rooted25["TOTAL"] !=0]
nzrooted26 = rooted26[rooted26["TOTAL"] !=0]

grnzbitrooted = grouping(nzbitrooted)
grnzrooted25 = grouping(nzrooted25)
grnzrooted26 = grouping(nzrooted26)

# Pestañas
tab1, tab2, tab3 = st.tabs(["Adjudicación Directa", "Institutos", "Proveedores"])

# Pestaña 1
with tab1:
    st.header("Resumen de Adjudicación Directa")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="resumen_abasto")
        abastecimiento = abasto_options[selected_abasto]
    with col2:
        selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="resumen_type")
        ty = type_options[selected_type]

    #col3, col4 = st.columns(2)
    with col3:
        clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="resumen_clave")
        cl = [clave_input] if clave_input != "TODAS LAS CLAVES" else claves_unicas
    with col4:
        periodo_input = st.selectbox("Ingrese el periodo de adjudicación", list(periodo_options.keys()), key="resumen_periodo")
    # Filtrar datos
    datos_filtradosbi = grnzbitrooted[(grnzbitrooted['CLAVES'].isin(cl)) & (grnzbitrooted['CLAVES'].isin(abastecimiento)) & (grnzbitrooted['CLAVES'].isin(ty))]
    datos_filtrados25 = grnzrooted25[(grnzrooted25['CLAVES'].isin(cl)) & (grnzrooted25['CLAVES'].isin(abastecimiento)) & (grnzrooted25['CLAVES'].isin(ty))]
    datos_filtrados26 = grnzrooted26[(grnzrooted26['CLAVES'].isin(cl)) & (grnzrooted26['CLAVES'].isin(abastecimiento)) & (grnzrooted26['CLAVES'].isin(ty))]
    
    datos_filbi = nzbitrooted[(nzbitrooted['CLAVES'].isin(cl)) & (nzbitrooted['CLAVES'].isin(abastecimiento)) & (nzbitrooted['CLAVES'].isin(ty))]
    datos_fil25 = nzrooted25[(nzrooted25['CLAVES'].isin(cl)) & (nzrooted25['CLAVES'].isin(abastecimiento)) & (nzrooted25['CLAVES'].isin(ty))]
    datos_fil26 = nzrooted26[(nzrooted26['CLAVES'].isin(cl)) & (nzrooted26['CLAVES'].isin(abastecimiento)) & (nzrooted26['CLAVES'].isin(ty))]

    if periodo_input == "BIANUAL":
        df1 = datos_filtradosbi
        df2 = datos_filbi
        df1T = "CANTIDAD DEMANDADA BIANUAL"
        df2T = "IMPORTE BIANUAL"
        qclaves_fil = datos_filbi['CLAVES'].nunique()
        claves_fil = datos_filbi['CLAVES'].unique()
        qprov_fil = datos_filbi['PROVEEDOR'].nunique()
        prov_fil = datos_filbi['PROVEEDOR'].unique()
        
        
    elif periodo_input == "2025":
        df1 = datos_filtrados25
        df2 = datos_fil25
        df1T = "CANTIDAD DEMANDADA 2025"
        df2T = "IMPORTE 2025"
        qclaves_fil = datos_filbi['CLAVES'].nunique()
        claves_fil = datos_filbi['CLAVES'].unique()
        qprov_fil = datos_fil25['PROVEEDOR'].nunique()
        prov_fil = datos_fil25['PROVEEDOR'].unique()

    else:
        df1 = datos_filtrados26
        df2 = datos_fil26
        df1T = "CANTIDAD DEMANDADA 2026"
        df2T = "IMPORTE 2026"
        qclaves_fil = datos_filbi['CLAVES'].nunique()
        claves_fil = datos_filbi['CLAVES'].unique()
        qprov_fil = datos_fil26['PROVEEDOR'].nunique()
        prov_fil = datos_fil26['PROVEEDOR'].unique()
        
    # Crear columnas
    col1, col2, col3 = st.columns(3)
    col1.metric("NÚMERO DE PROVEEDORES", f"{qprov_fil}")
    col1.metric("CLAVES ADJUDICADAS", f"{qclaves_fil}")
    col1.metric("IMPORTE TOTAL ADJUDICADO($)", f"{sum(calcular_monto(totales(bi))["MONTO TOTAL"])}")
    # Mostrar gráficos en columnas
    with col1:
        st.header("Abasto")
        st.altair_chart(make_donut(75, "Adjudicadas", "green"))
        st.header("Desabasto")
        st.altair_chart(make_donut(25, "No Adjudicadas", "red"))
        st.dataframe(prov_fil)

    with col2:

        st.header("Tipo de Clave Bianual")
        st.plotly_chart(crear_pie(df1), key="resumenbi_pie_oferta")
        st.header("Tipo de Abastecimiento Bianual")
        st.plotly_chart(crear_hist(df2), key="resumenbi_hist_oferta")
        
   #     st.dataframe(claves_fil)

    with col3:
        st.header(df1T)
        st.plotly_chart(Vvisual("TOTAL", df2), key=f"df1T")
        st.header(df2T)
        st.plotly_chart(VvisualMonto("TOTAL", df2), key=f"df2T")
    st.dataframe(df2)
# Pestaña 2
with tab2:
    st.header("CCINSHAE")
# columnas dashboard
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="instituto_abasto")
        abastecimiento = abasto_options[selected_abasto]
    with col2:    
        selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="instituto_type")
        ty = type_options[selected_type]
    with col3:   
        clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="instituto_clave")
        cl = [clave_input] if clave_input != "TODAS LAS CLAVES" else claves_unicas
    with col4:
        selected_instituto = st.selectbox("Ingrese el Instituto:", list(instituto_options.keys()), key="demanda_instituto")
        inst = instituto_options[selected_instituto]
    with col5:
        periodo_input = st.selectbox("Ingrese el periodo de adjudicación", list(periodo_options.keys()), key="instituto_periodo")
      # Filtrar datos
    instpref = rooted(filtrar_inst(inst))
    instf = nonz(rooted(filtrar_inst(inst)))
    datos_filtrados = instf[(instf['CLAVES'].isin(cl)) & (instf['CLAVES'].isin(abastecimiento)) & (instf['CLAVES'].isin(ty))]
    input_response = 75
    input_text = "Progreso"
    input_color = "blue"
    col1, col2, col3 = st.columns(3)
    col1.metric("NÚMERO DE PROVEEDORES", f"{instf['PROVEEDOR'].nunique()}")
    col1.metric("CLAVES ADJUDICADAS", f"{nclaves_unicas}")
    with col1:
        st.header("Abasto")
        st.altair_chart(make_donut(75, "Adjudicadas", "green"))
        st.header("Desabasto")
        st.altair_chart(make_donut(25, "No Adjudicadas", "red"))
    with col2:
        st.dataframe(instf['PROVEEDOR'].unique())

    with col3:
        st.header("Tipo de Clave")
        st.plotly_chart(crear_pie(datos_filtrados), key="instituto_pie_oferta")
        
        st.header("Tipo de Abastecimiento")
        st.plotly_chart(crear_hist(datos_filtrados), key="instituto_hist_oferta")
    col1, col2, col3= st.columns(3) 
    with col1:
        st.header("Canitdades bianual")
        figq25 = visual(list(filtrar_inst(inst).columns)[0], datos_filtrados)
        with st.container():
            for i, fig25 in enumerate(figq25):
                st.plotly_chart(fig25, key=f"fig25_{i}")
            st.header("Importe bianual")
            figm25 = visualMonto(list(filtrar_inst(inst).columns)[0], datos_filtrados)
        for j, fic25 in enumerate(figm25):
            st.plotly_chart(fic25, key=f"fic25_{j}")
    with col2:
        st.header("Cantidades 2025")
        figq26 = visual(list(filtrar_inst(inst).columns)[1], datos_filtrados)
        for k, fig26 in enumerate(figq26):
            st.plotly_chart(fig26, key=f"fig26_{k}")
        st.header("Importe 2025")
        figm26 = visualMonto(list(filtrar_inst(inst).columns)[1], datos_filtrados)
        for l, fic26 in enumerate(figm26):
            st.plotly_chart(fic26, key=f"fic26_{l}")
    with col3:
        st.header("Canitades 2026")
        figqbi = visual(list(filtrar_inst(inst).columns)[2], datos_filtrados)
        for h, figbi in enumerate(figqbi):
            st.plotly_chart(figbi, key=f"figbi_{h}")
        st.header("Importe 2026")
        figmbi = visualMonto(list(filtrar_inst(inst).columns)[2], datos_filtrados)
        for g, ficbi in enumerate(figmbi):
            st.plotly_chart(ficbi, key=f"ficbi_{g}")
    # Incluir información general   
    st.dataframe(datos_filtrados)
    
# Pestaña 3
with tab3:
    st.header("Proveedores")

    selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="proveedor_abasto")
    abastecimiento = abasto_options[selected_abasto]
    
    selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="proveedor_type")
    ty = type_options[selected_type]
    
    clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="proveedor_clave")
    cl = [clave_input] if clave_input != "TODAS LAS CLAVES" else claves_unicas

    selected_proveedor = st.selectbox("Ingrese el Proveedor:", list(proveedor_options.keys()), key="proveedor_instituto")
    prov = proveedor_options[selected_proveedor]

    
    # Filtrar datos
    instpref = rooted(filtrar_inst(inst))
    instf = nonz(rooted(filtrar_inst(inst)))
    datos_filtrados = instf[(instf['CLAVES'].isin(cl)) & (instf['CLAVES'].isin(abastecimiento)) & (instf['CLAVES'].isin(ty))]

    
    # Crear columnas
    col1, col2 = st.columns(2)
    
    # Mostrar gráficos en columnas
    with col1:
        st.header("Tipo de Clave")
        st.plotly_chart(crear_pie(datos_filtrados), key="prov_pie_oferta")
        
    with col2:
        st.header("Tipo de Abastecimiento")
        st.plotly_chart(crear_hist(datos_filtrados), key="prov_hist_oferta")
        
   # figures = visual(list(filtrar_inst(inst).columns)[0], datos_filtrados)
    #for j, fig in enumerate(figures):
     #   st.plotly_chart(fig, key=f"fig_{j}")
    # Incluir información general   
    st.dataframe(datos_filtrados)
    
# Incluir imagen como pie de página
st.image("footer.png", use_container_width=True)
