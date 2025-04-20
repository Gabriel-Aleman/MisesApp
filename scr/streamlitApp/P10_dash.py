from streamlit_extras.dataframe_explorer import dataframe_explorer
from procesarDatos import *
import streamlit as st

if 'my_bins' not in st.session_state:
    st.session_state.my_bins = 5

o = datos()
d = o.df.copy()

#SIDEBAR
#-------------------------------------------------------------------------------------------------------------------------------------
with st.sidebar:
    with st.popover("🪛 Configurar número de decimales"):
        #Cantidad de decimales con los que se quiere presentar los resultados:
        decimales = st.number_input(label="Decimales", value=3, min_value=0)


# MAIN:

st.html("<h1 style='color:white;padding-left:20px;background: linear-gradient(to right, #8b0000, #ff0000, #ffa07a); border-radius:10px 50px 50px 10px'>Dash-board<h1>")
tab1, tab2, tab3, tab4 = st.tabs(["🗃️ Selección de datos", "📊 Gastos e ingresos", "💵 Balance e intereses", "🪙 Planilla"])

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

        df_f_styled = o.styledDF(df_f.round(decimales))      # Decorar columna de aporte
        
        trans=o.gananciasPerdidas(df_f)

        ganancias_df    = o.colData(df_f, "Crédito", addDates=True)
        gastos_df       = o.colData(df_f, "Débito", addDates=True)
        
        st.dataframe(df_f_styled)

    try:
        #GANANCIAS Y PERDIDAS
        #-------------------------------------------------------------------------------------------------------------------------------------
        with tab2:
            #-----------------------------------------------------------------------------------------
            
            col1, col2 = st.columns([1,2])

            with col1:
                st.markdown("## Valores :")

                st.success(f"Ganancias: {round(trans["ganancias"],decimales)}")
                st.error(f"Gastos:      {round(trans["gastos"], decimales)}" )

                st.markdown("### Estádisticas :")
                with st.expander("Estadísticas"):
                    col01, col02 = st.columns(2)
                    with col01:
                        st.table(o.colStat(ganancias_df, "Crédito").round(decimales))
                    with col02:
                        st.table(o.colStat(gastos_df, "Débito").round(decimales))

            with col2:
                with st.container(key="cont"):
                    delta_trans =trans["ganancias"]-trans["gastos"]
                    st.metric(label="Aporte a balance", value=o.ultimoValorBalance(df_f), delta=round(delta_trans, decimales), border=True)

                    st.plotly_chart(o.graph_gananciasPerdidas(df_f))
            #-----------------------------------------------------------------------------------------
            
            #GRÁFICOS ADICIONALES
            with st.expander("📈 Gráficos"):
                #Ganacias
                box_ganancias       = o.boxPlot_Graph(ganancias_df, col="Crédito")
                violin_ganancias    = o.violinPlot_Graph(ganancias_df, col="Crédito")
                bar_ganancias       = o.barPlot_Graph(ganancias_df, col="Crédito")
                hist_ganancias = go.Figure()

                #Gastos
                box_gastos       = o.boxPlot_Graph(gastos_df, col="Débito", my_color=colores_plotly[1])
                violin_gastos    = o.violinPlot_Graph(gastos_df, col="Débito", my_color=colores_plotly[1])
                bar_gastos       = o.barPlot_Graph(gastos_df, col="Débito", my_color="Inferno")
                hist_gastos = go.Figure()


                #OPCIONES
                #######################################################################
                st.html("<h1 style='padding-left:10px;border: 3px solid #3498db; border-radius:50px'>Configuración:</h1>")
                
                with st.container(key="conf"):
                    colOpt1, colOpt2, colOpt3 = st.columns([1,1,3])        
                    with colOpt1:
                        selection = st.segmented_control("Cátegorías", ["Gastos", "Ingresos"], selection_mode="multi")
                    
                    with colOpt2:
                        box_enable  = st.checkbox("Boxplot")
                        bar_enable  = st.checkbox("Gráfico de barras")
                        hist_enable  = st.checkbox("Histograma")
                    with colOpt3:
                        if hist_enable: #Construir histograma a partir de bins
                        
                            my_bins  = st.number_input("Bins de histograma", value=30, min_value=2)
                            hist_gastos      = o.Hist_Graph(gastos_df, col="Débito", my_color=colores_plotly[1],  bins=my_bins)
                            hist_ganancias      = o.Hist_Graph(ganancias_df, col="Crédito", bins=my_bins)

                        if box_enable:
                            boxtype=st.radio("Tipo de boxplot", options=["Caja", "Violin"], horizontal=True)

                if not(box_enable) and not(bar_enable) and not(hist_enable):
                            st.warning("⚠️ Por favor seleccione una opción de gráfico")
                
                #######################################################################
                if (box_enable or bar_enable or hist_enable) and (len(selection)!=0):
                    st.html("<h1 style='padding-left:10px;border: 3px solid red; border-radius:50px'>Gráficos:</h1>")
                
                if ("Gastos" in selection) and ("Ingresos" in selection):
                    colRes1, colRes2 = st.columns(2)
                    with colRes1:
                        if box_enable:
                            grafico_box = box_gastos if boxtype=="Caja" else violin_gastos
                            st.plotly_chart(grafico_box)

                        if bar_enable:
                            st.plotly_chart(bar_gastos)

                        if hist_enable:
                            st.plotly_chart(hist_gastos)
                    
                    with colRes2:
                        if box_enable:
                            grafico_box = box_ganancias if boxtype=="Caja" else violin_ganancias
                            st.plotly_chart(grafico_box)

                        if bar_enable:
                            st.plotly_chart(bar_ganancias)

                        if hist_enable:
                            st.plotly_chart(hist_ganancias)
                else:
                    if ("Gastos" not in selection) and ("Ingresos" not in selection):
                        st.warning("⚠️ Por favor seleccione una de las categorías")
                    else:
                        if ("Gastos" in selection):
                                box_sel     = box_gastos    
                                violin_sel  = violin_gastos    
                                bar_sel     = bar_gastos    
                                hist_sel    = hist_gastos
                        else:
                                box_sel     = box_ganancias    
                                violin_sel  = violin_ganancias    
                                bar_sel     = bar_ganancias    
                                hist_sel    = hist_ganancias
                        
                        if box_enable:
                            grafico_box = box_sel if boxtype=="Caja" else violin_sel
                            st.plotly_chart(grafico_box)

                        if bar_enable:
                            st.plotly_chart(bar_sel)

                        if hist_enable:
                            st.plotly_chart(hist_sel)                       
        with tab3:
            st.plotly_chart(o.graph_BalanceXTime(df_f))
            st.plotly_chart(o.graph_IntXTime(df_f))
        with tab4:
            st.plotly_chart(o.Planillas(df_f))


        #---------------------------------------------------------------------------------------
    except:
        pass