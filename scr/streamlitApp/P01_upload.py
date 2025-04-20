from streamlit_option_menu import option_menu
from procesarDatos import *
from io import StringIO
import streamlit as st
import time
st.html("<h1 style='color:white;padding-left:20px;background: linear-gradient(to right, #8b0000, #ff0000, #ffa07a); border-radius:10px 50px 50px 10px'>Cargar información a DB<h1>")

with st.sidebar:
    selected = option_menu("Opciones", ["Cargar desde CSV", 'Cargar manualmente'], 
        icons=['cloud-upload-fill', 'pencil-square'], menu_icon="gear", default_index=0)

#CARGAR DATO DESDE ARCHIVO:
#............................................................................................
if selected == "Cargar desde CSV":
    file=st.file_uploader("Ingrese un archivo", type="csv")

    if file is not None:
        stringio    = StringIO(file.getvalue().decode("latin1"))
        string_data = stringio.read()

        o = datos(selectMode=False, stringData=string_data, readFromDB=False)
        st.write(o.df)


        nuevasDescripciones= o.nuevasCategorias()
        num_nuevasDescripciones = len(nuevasDescripciones)

        if num_nuevasDescripciones>0:
            st.warning(f":warning: Se han encontrado {num_nuevasDescripciones} descripciones que no están en la base de datos")
        
        if st.button(":arrow_down: Actualizar en la base de datos"):
            with st.spinner("Actualizando"):
                o.write_hist2DB()

                for i in nuevasDescripciones: #Agregar las nuevas categorías a la DB
                    o.agregarDescripcion(i)
            
            st.success("Datos cargados exitosamente")
#CARGAR DATO MANUALMENTE:
#............................................................................................
else:
    o = datos()
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