from streamlit_elements import elements, mui, html
import streamlit as st
from procesarDatos import *
decimales = 3
o = datos()
tab1, tab2, tab3 = st.tabs(["📈 Chart", "🗃 Gastos e ingresos", "Balance"])
d = o.df

with st.sidebar:
    """TODO: Agregar opciones de filtrado"""

with tab1:
    st.write(o.styledDF(d))

with tab2:
    trans=o.gananciasPerdidas()
    col1, col2 = st.columns([1,2])
    with col1:
        with st.container(border=True):
            st.markdown("### Valores :")

            st.success(f"Ganancias: {round(trans["ganancias"],decimales)}")
            st.error(f"Gastos: {round(trans["gastos"], decimales)}" )
            st.markdown("### Estádisticas :")
            col01, col02 = st.columns(2)
            with col01:
                st.dataframe(o.colStat("Crédito"))
            with col02:
                st.dataframe(o.colStat("Débito"))

    with col2:
        st.plotly_chart(o.graph_gananciasPerdidas())
    st.plotly_chart(o.disp_GastosYGanancias("Crédito"))
    #st.plotly_chart(o.boxPlot_GastosYGanancias())
with tab3:
    st.plotly_chart(o.graph_BalanceXTime())