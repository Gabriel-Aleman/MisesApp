import streamlit as st
from io import StringIO
from procesarDatos import *

st.html("<h1 style='color:white;padding-left:20px;background: linear-gradient(to right, #8b0000, #ff0000, #ffa07a); border-radius:10px 50px 50px 10px'>Cargar archivo de estado financieros<h1>")

file=st.file_uploader("Ingrese un archivo", type="csv")

if file is not None:
    stringio = StringIO(file.getvalue().decode("utf-8"))
    # To read file as string:
    string_data = stringio.read()

    o = datos(selectMode=False, stringData=string_data, readFromDB=False)
    st.write(o.styledDF())

    nuevasDescripciones= o.nuevasCategorias()
    num_nuevasDescripciones = len(nuevasDescripciones)

    if num_nuevasDescripciones>0:
        st.warning(f":warning: Se han encontrado {num_nuevasDescripciones} descripciones que no están en la base de datos")
    
    st.button(":arrow_down: Actualizar en la base de datos")