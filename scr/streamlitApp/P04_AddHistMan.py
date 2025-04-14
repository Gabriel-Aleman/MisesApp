from streamlit.components.v1 import html
from procesarDatos import *
import time

o = datos()

st.header("Ingresar dato manualmente", divider=True)
with st.container(border=True):
    date    = st.date_input("Fecha")
    ref     = st.text_input("Referencia")
    cod     = st.number_input("Código",value=0, min_value=0)
    desc    = st.text_area("Descripción")
    col1, col2 = st.columns([3,1])
    with col2:
        tipo    = st.radio("Tipo de monto", options=[":red[Crédito]", ":blue[Débito]"], horizontal=True)
    with col1:
        monto   = st.number_input("Monto",value=0.0)
    
    balance = st.number_input("Balance",value=0, min_value=0)

col1, col2 = st.columns(2)

tipo_trans = bool(tipo == ":blue[Débito]")

with col2:
    conf=not(st.checkbox("Confirmar cambio"))
with col1:
    if st.button("💾 Guardar nuevo registro en historial", disabled=conf):
        try:
            o.write_histConTipo(date, ref, cod, desc, monto, balance, tipo_trans)
        except:
            st.error("Hubo un error cargando el nuevo registro")
        else:
            st.success("El registro se guardó con éxito")
            time.sleep(3)
            st.rerun()