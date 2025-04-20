from streamlit_extras.dataframe_explorer import dataframe_explorer
from procesarDatos import *
import streamlit as st

if 'my_bins' not in st.session_state:
    st.session_state.my_bins = 5

o = datos()
d = o.dataFrame_Categorias()
#SIDEBAR
#-------------------------------------------------------------------------------------------------------------------------------------
with st.sidebar:
    with st.popover("🪛 Configurar número de decimales"):
        #Cantidad de decimales con los que se quiere presentar los resultados:
        decimales = st.number_input(label="Decimales", value=3, min_value=0)


# MAIN:

st.html("<h1 style='color:white;padding-left:20px;background: linear-gradient(to right, #8b0000, #ff0000, #ffa07a); border-radius:10px 50px 50px 10px'>Analísis x Categorías<h1>")
tab1, tab2, tab3, tab4 = st.tabs(["🗃️ Selección de datos", "🔢 Estádisticas", "💳 Gastos x Categoría", "💲 Distribución de los datos"])

if len(d)==0:
    st.error("Actualmente sin datos")

else:
    #FILTRAR DF:
    #-------------------------------------------------------------------------------------------------------------------------------------
    with tab1:
        with st.expander("🔎 Opciones de filtrado"):
            desde =hasta = hoy
            colOpciones1, colOpciones2 = st.columns([1,2])
            with colOpciones1:
                with st.popover("Date-Range"):
                    dateRange=st.pills("Rango de fechas", options=["Todos los registros", "Semana anterior", "Mes anterior"], default="Todos los registros")


            with colOpciones2:
                if dateRange!="Todos los registros" and dateRange is not None:
                    if (dateRange=="Semana anterior"):
                        desde, hasta = semanaAnterior()
                    elif (dateRange=="Mes anterior"):
                        desde, hasta = mesAnterior()
                    st.success(f"Desde {desde} hasta {hasta}")
                    d = d.query("Fechas >= @desde and Fechas <= @hasta")
                else:
                    st.success(f"Todos los registros")

            df_f = dataframe_explorer(d)    # Data frame filtrado
            st.info(f"{len(df_f)} resultados en la busqueda")
        estad = o.dataFrame_Categorias_Stad(df_f)
        st.write(df_f) 

    try:
        with tab2:
            columnas_estad=["Categoría"]
            with st.expander("Información a visualizar"):
                opt=["Suma", "Promedio", "Cantidad", "Mínimo", "Máximo","Mediana","Desviación estándar", "Varianza"]
                columnas_estad_opt = st.pills("Datos", options=opt, selection_mode = "multi", default=opt[0:5])
            columnas_estad.extend(columnas_estad_opt)
            st.dataframe(estad[columnas_estad])

        with tab3:
            st.markdown("### Gastos por categoría:")
            st.bar_chart(estad, x="Categoría", y="Suma", color="Categoría", height=500)
            st.markdown("----")

            st.plotly_chart(o.cat_PiePlot(estad))
        #---------------------------------------------------------------------------------------
        with tab4:
            st.plotly_chart(o.cat_BoxPlot(df_f))
            st.plotly_chart(o.cat_ScatPlot(df_f))

    except:
        pass