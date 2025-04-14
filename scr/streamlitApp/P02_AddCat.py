import streamlit as st
from io import StringIO
from streamlit.components.v1 import html
from procesarDatos import *
import time

if 'success' not in st.session_state:
    st.session_state.success = False
if 'visibility' not in st.session_state:
    st.session_state.visibility = False


o = datos()
catList=o.read_catList()
st.html("<h1 style='color:white;padding-left:20px;background: linear-gradient(to right, #8b0000, #ff0000, #ffa07a); border-radius:10px 50px 50px 10px'>Agrerar nueva categoria<h1>")
newCat=st.text_input("Ingrese el nombre de la nueva categoría:")

col1, col2 = st.columns([2,1])
typeErr =""
with col1:
    if st.button(":pencil2: Añadir categoría base de datos"):
        st.session_state.visibility = True
        
        if newCat in catList: #Verificar que no esté ya en la lista de categorías ni sea una cadena de caracteres en blanco
            typeErr="cat"
            st.session_state.success = False

        elif stringVacio(newCat):
            typeErr="empty"
            st.session_state.success = False

        else: 
            st.session_state.success = True

with col2:
    with st.popover("Lista de categorías"):
        st.write(catList)

if (st.session_state.visibility ):
    if not(st.session_state.success):
        st.warning("No se pudo agregar la categoría")

        match typeErr:
            case "empty":
                html("<script>alert('Categoría no puede ser una cadena de caracteres vacios')</script>")

            case "cat":
                html("<script>alert('Categoría ya en uso')</script>")
                

    else:
        if st.button("✅ Confimar cambio"):
            try:
                o.agregarCategoria(newCat)
            except:
                st.error("No se pudo añadir la nueva categoría")
            else:
                st.success("Categoría añadida con exito")
                time.sleep(5)
                try:
                    st.session_state.visibility = False
                except:
                    pass
                else:
                    st.rerun()