import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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
        data = data.copy()
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

def tentop_prov(data):
    provider_counts = df['PROVEEDOR'].value_counts()
    proveedores_unicos = df['PROVEEDOR'].unique()
    counts_list = [provider_counts[provider] for provider in proveedores_unicos]
    cuentas = pd.DataFrame({'PROVEEDOR': proveedores_unicos, 'CUENTA': counts_list})
    cuenta = cuentas.sort_values(by='PROVEEDOR')

    monprov = rooted(totales(calcular_monto(data)))
    impprov = monprov.groupby("PROVEEDOR").sum().reset_index()
    sortprov=impprov.sort_values('PROVEEDOR')
    top = sortprov.sort_values("TOTAL").tail(10)
    topsorted = top.sort_values("PROVEEDOR")
    
    ten = cuenta[cuenta['PROVEEDOR'].isin(top['PROVEEDOR'])]
    
    tentop = pd.DataFrame({'PROVEEDOR': ten['PROVEEDOR'].reset_index(drop=True), 'CUENTA': ten['CUENTA'].reset_index(drop=True), 'IMPORTE': topsorted['TOTAL'].reset_index(drop=True)})
    return tentop
    
def instxproveer(dats, proveedor):
    # Filtrar el DataFrame para el proveedor dado
    data = pd.concat([df['PROVEEDOR'],dats], axis=1)
    df_proveedor = data[data['PROVEEDOR'] == proveedor]
    # Obtener las columnas con valores distintos de cero
    columnas_distintas_de_cero = df_proveedor.loc[:, (df_proveedor != 0).any(axis=0)].columns.tolist()
    # Excluir las columnas 'PROVEEDOR' y '#'
    columnas_distintas_de_cero = [col for col in columnas_distintas_de_cero if col not in ['PROVEEDOR', '#']]
    return columnas_distintas_de_cero

# Definimos funciones para crear gráficos
def crear_pie(data):
    data['Tipo'] = data['CLAVES'].apply(lambda x: 'Medicamento' if int(x.split('.')[0]) < 60 else 'Material de Curación')
    return px.pie(data, names='Tipo', color='Tipo', color_discrete_map={'Medicamento': 'blue', 'Material de Curación': 'red'}, width=400, height=400)

def crear_hist(data):
    data['Tipo'] = data['ABASTO'].apply(lambda x: 'Abastecimiento único' if x == 1 else 'Abastecimiento simultáneo')
    fig = px.histogram(data, x='Tipo', color='Tipo', color_discrete_map={'Abastecimiento único': 'green', 'Abastecimiento simultáneo': 'yellow'}, width=400, height=400)
    fig.add_annotation(
        text="* El abastecimiento simultáneo se cuenta con multiplicidad",
        xref="paper", yref="paper",
        x=0.5, y=-.45,
        showarrow=False,
        font=dict(size=12)
    )
    return fig

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
    return fig

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

import plotly.express as px

def cloud_bubbles_prov(data):
    tentop = tentop_prov(data)
    
    factor = 50000  # Factor para reducir el tamaño de los puntos
    tentop['IMPORTE_REDUCIDO'] = tentop['IMPORTE'] / factor
    
    fig = px.scatter(
        tentop,
        x='PROVEEDOR',
        y='CUENTA',
        size='IMPORTE_REDUCIDO',  # Tamaño de los puntos basado en el valor reducido
        color='IMPORTE',  # Color basado en el valor original
        hover_name='PROVEEDOR',
        size_max=60,
        color_continuous_scale='Viridis',
        title='Importe total por proveedor'
    )
    
    fig.update_layout(
        xaxis_title='Proveedor',
        yaxis_title='Cantidad de claves adjudicadas',
        coloraxis_colorbar=dict(
            title='IMPORTE TOTAL ($)',
            tickformat=',.0f'  # Formato de los valores en la barra de colores
        )
    )
    
    return fig


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
#monto
df2025 = pd.concat([df5, totales(calcular_monto(df5))], axis=1)
df2026 = pd.concat([df6, totales(calcular_monto(df6))], axis=1)
bitmoon  = pd.concat([bi, totales(calcular_monto(bi))], axis=1)

bitrooted = rooted(bit)
rooted25 = rooted(df25)
rooted26 = rooted(df26)
#monto
bitmoonrooted = rooted(bitmoon)
rooted2025 = rooted(df2025)
rooted2026 = rooted(df2026)

nzbitrooted = bitrooted[bitrooted["TOTAL"] !=0]
nzrooted25 = rooted25[rooted25["TOTAL"] !=0]
nzrooted26 = rooted26[rooted26["TOTAL"] !=0]
#monto
nzbitmoonrooted = bitmoonrooted[bitmoonrooted["TOTAL"] !=0]
nzrooted2025 = rooted2025[rooted25["TOTAL"] !=0]
nzrooted2026 = rooted2026[rooted26["TOTAL"] !=0]

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
        c_selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="resumen_abasto")
        c_abastecimiento = abasto_options[c_selected_abasto]
    with col2:
        c_selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="resumen_type")
        c_ty = type_options[c_selected_type]

    #col3, col4 = st.columns(2)
    with col3:
        c_clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="resumen_clave")
        c_cl = [c_clave_input] if c_clave_input != "TODAS LAS CLAVES" else claves_unicas
    with col4:
        cl_periodo_input = st.selectbox("Ingrese el periodo de adjudicación", list(periodo_options.keys()), key="resumen_periodo")
    # Filtrar datos
    datos_filtradosbi = grnzbitrooted[(grnzbitrooted['CLAVES'].isin(c_cl)) & (grnzbitrooted['CLAVES'].isin(c_abastecimiento)) & (grnzbitrooted['CLAVES'].isin(c_ty))]
    datos_filtrados25 = grnzrooted25[(grnzrooted25['CLAVES'].isin(c_cl)) & (grnzrooted25['CLAVES'].isin(c_abastecimiento)) & (grnzrooted25['CLAVES'].isin(c_ty))]
    datos_filtrados26 = grnzrooted26[(grnzrooted26['CLAVES'].isin(c_cl)) & (grnzrooted26['CLAVES'].isin(c_abastecimiento)) & (grnzrooted26['CLAVES'].isin(c_ty))]
    
    datos_filbi = nzbitrooted[(nzbitrooted['CLAVES'].isin(c_cl)) & (nzbitrooted['CLAVES'].isin(c_abastecimiento)) & (nzbitrooted['CLAVES'].isin(c_ty))]
    datos_fil25 = nzrooted25[(nzrooted25['CLAVES'].isin(c_cl)) & (nzrooted25['CLAVES'].isin(c_abastecimiento)) & (nzrooted25['CLAVES'].isin(c_ty))]
    datos_fil26 = nzrooted26[(nzrooted26['CLAVES'].isin(c_cl)) & (nzrooted26['CLAVES'].isin(c_abastecimiento)) & (nzrooted26['CLAVES'].isin(c_ty))]

    datos_moon_bi = nzbitmoonrooted[(nzbitmoonrooted['CLAVES'].isin(c_cl)) & (nzbitmoonrooted['CLAVES'].isin(c_abastecimiento)) & (nzbitmoonrooted['CLAVES'].isin(c_ty))]
    datos_moon_25 = nzrooted2025[(nzrooted2025['CLAVES'].isin(c_cl)) & (nzrooted2025['CLAVES'].isin(c_abastecimiento)) & (nzrooted2025['CLAVES'].isin(c_ty))]
    datos_moon_26 = nzrooted2026[(nzrooted2026['CLAVES'].isin(c_cl)) & (nzrooted2026['CLAVES'].isin(c_abastecimiento)) & (nzrooted2026['CLAVES'].isin(c_ty))]
    
    if cl_periodo_input == "BIANUAL":
        df1 = datos_filtradosbi
        df2 = datos_filbi
        df3 = datos_moon_bi
        df1T = "CANTIDADES BIANUAL"
        df2T = "IMPORTE BIANUAL"
        qclaves_fil = datos_filbi['CLAVES'].nunique()
        claves_fil = datos_filbi['CLAVES'].unique()
        qprov_fil = datos_filbi['PROVEEDOR'].nunique()
        prov_fil = datos_filbi['PROVEEDOR'].unique()
        
        
    elif cl_periodo_input == "2025":
        df1 = datos_filtrados25
        df2 = datos_fil25
        df3 = datos_moon_25
        df1T = "CANTIDADES 2025"
        df2T = "IMPORTE 2025"
        qclaves_fil = datos_fil25['CLAVES'].nunique()
        claves_fil = datos_fil25['CLAVES'].unique()
        qprov_fil = datos_fil25['PROVEEDOR'].nunique()
        prov_fil = datos_fil25['PROVEEDOR'].unique()

    else:
        df1 = datos_filtrados26
        df2 = datos_fil26
        df3 = datos_moon_26
        df1T = "CANTIDADES 2026"
        df2T = "IMPORTE 2026"
        qclaves_fil = datos_fil26['CLAVES'].nunique()
        claves_fil = datos_fil26['CLAVES'].unique()
        qprov_fil = datos_fil26['PROVEEDOR'].nunique()
        prov_fil = datos_fil26['PROVEEDOR'].unique()
        
    # Crear columnas
    col1, col2, col3 = st.columns(3)
    col1.metric("NÚMERO DE PROVEEDORES", f"{qprov_fil}")
    col1.metric("CLAVES ADJUDICADAS", f"{qclaves_fil}")
    col1.metric("IMPORTE TOTAL ADJUDICADO ($)", f"{"{:,.2f}".format(sum(df3["TOTAL"]))}")
    # Mostrar gráficos en columnas
    with col1:
        st.header("ABASTO / DESABASTO")
        col11, col12 = st.columns(2)
        with col11:
            st.altair_chart(make_donut(75, "Adjudicadas", "green"))
        with col12:
            st.altair_chart(make_donut(25, "No Adjudicadas", "red"))
        st.header("PROVEEDORES ADJUDICADOS")
        st.dataframe(prov_fil)

    with col2:

        st.header("Tipo de Clave")
        st.plotly_chart(crear_pie(df1), key="resumenbi_pie_oferta")
        st.header("Tipo de Abastecimiento")
        st.plotly_chart(crear_hist(df2), key="resumenbi_hist_oferta")
        
   #     st.dataframe(claves_fil)

    with col3:
        st.header(df1T)
        st.plotly_chart(Vvisual("TOTAL", df2), key=f"df1T")
        st.header(df2T)
        st.plotly_chart(VvisualMonto("TOTAL", df3), key=f"df2T")
    st.header("INFO")
    st.dataframe(df2)
# Pestaña 2
with tab2:
    st.header("CCINSHAE")
# columnas dashboard
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        hi_selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="instituto_abasto")
        hi_abastecimiento = abasto_options[hi_selected_abasto]
    with col2:    
        hi_selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="instituto_type")
        hi_ty = type_options[hi_selected_type]
    with col3:   
        hi_clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="instituto_clave")
        hi_cl = [hi_clave_input] if hi_clave_input != "TODAS LAS CLAVES" else claves_unicas
    with col4:
        hi_selected_instituto = st.selectbox("Ingrese el Instituto:", list(instituto_options.keys()), key="demanda_instituto")
        inst = instituto_options[hi_selected_instituto]
    with col5:
        hi_periodo_input = st.selectbox("Ingrese el periodo de adjudicación", list(periodo_options.keys()), key="instituto_periodo")
      # Filtrar datos

    if hi_periodo_input == "BIANUAL":
        hi1T = "CANTIDADES BIANUAL"
        hi2T = "IMPORTE BIANUAL"
        i = 2
        name = inst+"_25-26"
    elif hi_periodo_input == "2025":
        hi1T = "CANTIDADES 2025"
        hi2T = "IMPORTE 2025"
        i = 0
        name = inst+"_25"
    else:
        hi1T = "CANTIDADES 2026"
        hi2T = "IMPORTE 2026"
        i = 1
        name = inst+"_26"
    hi1 = grouping(nonz(rooted(filtrar_inst(inst).iloc[:,[i]])))
    hi2 = nonz(rooted(filtrar_inst(inst).iloc[:,[i]]))
    hi3 =nonz(rooted(calcular_monto(filtrar_inst(inst).iloc[:,[i]])))
    hi4 = hi2
    hi5 = hi4[(hi4['CLAVES'].isin(hi_cl)) & (hi4['CLAVES'].isin(hi_abastecimiento)) & (hi4['CLAVES'].isin(hi_ty))]
    
    qclaves_hi = hi5['CLAVES'].nunique()
    claves_hi = hi5['CLAVES'].unique()
    qprov_hi = hi5['PROVEEDOR'].nunique()
    prov_hi = hi5['PROVEEDOR'].unique()
        
    col1, col2, col3 = st.columns(3)
    col1.metric("NÚMERO DE PROVEEDORES", f"{qprov_hi}")
    col1.metric("CLAVES ADJUDICADAS", f"{qclaves_hi}")
    col1.metric("IMPORTE TOTAL ADJUDICADO ($)", f"{"{:,.2f}".format(sum(hi5[name]))}")
    with col1:
        st.header("Proveedores adjudicados")
        st.dataframe(hi5['PROVEEDOR'].unique())
    with col2:
        st.header(hi1T)
        hi4=hi2
        st.plotly_chart(Vvisual(name, hi5), key=f"hi1T")
        st.header(hi2T)
        hi4=hi3
        st.plotly_chart(VvisualMonto(name, hi5), key=f"hi2T")

    with col3:
        hi4=hi2
        st.header("Tipo de Clave")
        st.plotly_chart(crear_pie(hi5), key="instituto_pie_oferta")
        hi4=hi2
        st.header("Tipo de Abastecimiento")
        st.plotly_chart(crear_hist(hi5), key="instituto_hist_oferta")

    hi4=hi2
    st.dataframe(hi5)
    
# Pestaña 3
with tab3:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        p_selected_abasto = st.selectbox("Ingrese tipo de abastecimiento", list(abasto_options.keys()), key="proveedor_abasto")
        p_abastecimiento = abasto_options[p_selected_abasto]
    with col2:    
        p_selected_type = st.selectbox("Ingrese el tipo de clave", list(type_options.keys()), key="proveedor_type")
        p_ty = type_options[p_selected_type]
    with col3:   
        p_clave_input = st.selectbox("Ingrese la clave", list(clave_options.keys()), key="proveedor_clave")
        p_cl = [p_clave_input] if p_clave_input != "TODAS LAS CLAVES" else claves_unicas
    with col4:
        p_selected_proveedor = st.selectbox("Ingrese el Proveedor:", list(proveedor_options.keys()), key="adj_proveedor")
      #  p_inst = instituto_options[selected_instituto]            borrar linea
    with col5:
        p_periodo_input = st.selectbox("Ingrese el periodo de adjudicación", list(periodo_options.keys()), key="proveedor_periodo")
        
    prov_filtradosbi = grnzbitrooted[(grnzbitrooted['CLAVES'].isin(p_cl)) & (grnzbitrooted['CLAVES'].isin(p_abastecimiento)) & (grnzbitrooted['CLAVES'].isin(p_ty))]
    prov_filtrados25 = grnzrooted25[(grnzrooted25['CLAVES'].isin(p_cl)) & (grnzrooted25['CLAVES'].isin(p_abastecimiento)) & (grnzrooted25['CLAVES'].isin(p_ty))]
    prov_filtrados26 = grnzrooted26[(grnzrooted26['CLAVES'].isin(p_cl)) & (grnzrooted26['CLAVES'].isin(p_abastecimiento)) & (grnzrooted26['CLAVES'].isin(p_ty))]
    
    prov_filbi = nzbitrooted[(nzbitrooted['CLAVES'].isin(p_cl)) & (nzbitrooted['CLAVES'].isin(p_abastecimiento)) & (nzbitrooted['CLAVES'].isin(p_ty))]
    prov_fil25 = nzrooted25[(nzrooted25['CLAVES'].isin(p_cl)) & (nzrooted25['CLAVES'].isin(p_abastecimiento)) & (nzrooted25['CLAVES'].isin(p_ty))]
    prov_fil26 = nzrooted26[(nzrooted26['CLAVES'].isin(p_cl)) & (nzrooted26['CLAVES'].isin(p_abastecimiento)) & (nzrooted26['CLAVES'].isin(p_ty))]

    prov_moon_bi = nzbitmoonrooted[(nzbitmoonrooted['CLAVES'].isin(p_cl)) & (nzbitmoonrooted['CLAVES'].isin(p_abastecimiento)) & (nzbitmoonrooted['CLAVES'].isin(p_ty))]
    prov_moon_25 = nzrooted2025[(nzrooted2025['CLAVES'].isin(p_cl)) & (nzrooted2025['CLAVES'].isin(p_abastecimiento)) & (nzrooted2025['CLAVES'].isin(p_ty))]
    prov_moon_26 = nzrooted2026[(nzrooted2026['CLAVES'].isin(p_cl)) & (nzrooted2026['CLAVES'].isin(p_abastecimiento)) & (nzrooted2026['CLAVES'].isin(p_ty))]
    
    if p_periodo_input == "BIANUAL":
        prov1 = prov_filtradosbi[prov_filtradosbi["PROVEEDOR"]==p_selected_proveedor]
        prov2 = prov_filbi[ prov_filbi["PROVEEDOR"]==p_selected_proveedor]
        prov3 = prov_moon_bi[prov_moon_bi["PROVEEDOR"]==p_selected_proveedor]
        prov4 = bi
        prov1T = "CANTIDADES BIANUAL"
        prov2T = "IMPORTE BIANUAL"
        prov_qclaves_fil = prov2['CLAVES'].nunique()
        prov_claves_fil = prov2['CLAVES'].unique()
        prov_qprov_fil = prov2['PROVEEDOR'].nunique()
        prov_prov_fil = prov2['PROVEEDOR'].unique()
        
        
    elif p_periodo_input == "2025":
        prov1 = prov_filtrados25[prov_filtrados25["PROVEEDOR"]==p_selected_proveedor]
        prov2 = prov_fil25[prov_fil25["PROVEEDOR"]==p_selected_proveedor]
        prov3 = prov_moon_25[prov_moon_25["PROVEEDOR"]==p_selected_proveedor]
        prov4 = df5
        prov1T = "CANTIDADES 2025"
        prov2T = "IMPORTE 2025"
        prov_qclaves_fil = prov2['CLAVES'].nunique()
        prov_claves_fil = prov2['CLAVES'].unique()
        prov_qprov_fil = prov2['PROVEEDOR'].nunique()
        prov_prov_fil = prov2['PROVEEDOR'].unique()

    else:
        prov1 = prov_filtrados26[prov_filtrados26["PROVEEDOR"]==p_selected_proveedor]
        prov2 = prov_fil26[prov_fil26["PROVEEDOR"]==p_selected_proveedor]
        prov3 = prov_moon_26[prov_moon_26["PROVEEDOR"]==p_selected_proveedor]
        prov4 = df6
        prov1T = "CANTIDADES 2026"
        prov2T = "IMPORTE 2026"
        prov_qclaves_fil = prov2['CLAVES'].nunique()
        prov_claves_fil = prov2['CLAVES'].unique()
        prov_qprov_fil = prov2['PROVEEDOR'].nunique()
        prov_prov_fil = prov2['PROVEEDOR'].unique()
    col18, col19 = st.columns([0.60, 0.40])
    with col18:
        st.header("TOP 10 PROVEEDORES CON MAYOR IMPORTE")
        st.plotly_chart(cloud_bubbles_prov(prov4), key="prov-top10")
    with col19:
        provider_adjs = rooted(prov4)['PROVEEDOR'].value_counts()
        tlist = [provider_adjs[provider] for provider in proveedores_unicos]
        t10 = pd.DataFrame({'PROVEEDOR': proveedores_unicos, 'CUENTA': tlist})
        tt = t10.sort_values(by='CUENTA')
        tt = tt.tail(10)
        fig, ax = plt.subplots(figsize=(12, 12))
        bars = ax.barh(tt['PROVEEDOR'], tt['CUENTA'], color='skyblue')
        ax.set_xlabel('Número de Claves', fontsize=24)
        ax.set_ylabel('Proveedor', fontsize=24)
        ax.set_title('Top 10 Proveedores con Más Claves Adjudicadas', fontsize=24)
        ax.tick_params(axis='x', labelsize=18)
        ax.tick_params(axis='y', labelsize=18)
        for bar in bars:
            ax.annotate(f'{bar.get_width()}', xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2), xytext=(5, 0), textcoords='offset points', ha='left', va='center', fontsize=18)
        st.header("TOP 10 PROVEEDORES CON MÁS ADJUDICACIONES")
        st.pyplot(fig)
    
    col1, col2, col3 = st.columns(3)
   # col1.metric("NÚMERO DE PROVEEDORES", f"{prov_qprov_fil}")
    col1.metric("CLAVES ADJUDICADAS", f"{prov_qclaves_fil}")
    col1.metric("IMPORTE TOTAL ADJUDICADO($)", f"{"{:,.2f}".format(sum(prov3["TOTAL"]))}")
    # Mostrar gráficos en columnas
    with col1:
        inst_a_proveer = instxproveer(prov4, p_selected_proveedor)
        st.header(f"INSTITUTOS A PROVEER POR {p_selected_proveedor}:")
        st.table(pd.DataFrame(inst_a_proveer, columns=['Instituos']))

    with col2:

        st.header("Tipo de Clave")
        st.plotly_chart(crear_pie(prov1), key="prov_pie_oferta")
        st.header("Tipo de Abastecimiento")
        st.plotly_chart(crear_hist(prov2), key="prov_hist_oferta")
        
   #     st.dataframe(prov_claves_fil)

    with col3:
        st.header(prov1T)
        st.plotly_chart(Vvisual("TOTAL", prov2), key=f"prov1T")
        st.header(prov2T)
        st.plotly_chart(VvisualMonto("TOTAL", prov3), key=f"prov2T")
    st.header("INFO")
    st.dataframe(prov2)

    
    # Crear columnas
    col1, col2 = st.columns(2)
    
    # Mostrar gráficos en columnas
   # with col1:
    #    st.header("Tipo de Clave")
     #   st.plotly_chart(crear_pie(datos_filtrados), key="prov_pie_oferta")
        
    #with col2:
     #   st.header("Tipo de Abastecimiento")
      #  st.plotly_chart(crear_hist(datos_filtrados), key="prov_hist_oferta")
        
    

    #st.dataframe(datos_filtrados)
    
# Incluir imagen como pie de página
st.image("footer.png", use_container_width=True)
