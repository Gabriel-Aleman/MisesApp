from streamlit_option_menu import option_menu
from streamlit.components.v1 import html
from procesarDatos import *
import streamlit as st
import time

if 'success' not in st.session_state:
    st.session_state.success = False
if 'visibility' not in st.session_state:
    st.session_state.visibility = False


#VARIABLES GLOBALES:
#----------------------------------------------------------------------------------
exitoEliminacion = False
tiempo_reset = 3 # En segundos
#----------------------------------------------------------------------------------

st.html("<h1 style='color:white;padding-left:20px;background: linear-gradient(to right, #8b0000, #ff0000, #ffa07a); border-radius:10px 50px 50px 10px'>Agrerar y eliminar categorias<h1>")

with st.sidebar:
    selected = option_menu("Opciones", ["Agregar categoría", 'Eliminar categoría'], 
        icons=['clipboard-plus', 'trash-fill'], menu_icon="gear", default_index=0)

o = datos()

#AGREGAR CATEGORÍA:
#----------------------------------------------------------------------------------
if selected == "Agregar categoría":
    catList=o.read_catList()
    newCat=st.text_input("Ingrese el nombre de la nueva categoría:") #Categoría a añadir
    newCat=newCat.strip() #Eliminar espacios vacios al final o inicio

    col1, col2 = st.columns([2,1])
    typeErr =""

    with col1:
        if st.button(":pencil2: Añadir categoría base de datos"):
            st.session_state.visibility = True
            
            #Verificar que no esté ya en la lista de categorías
            if newCat in catList: 
                typeErr="cat"
                st.session_state.success = False

            #Verificar qye no sea una cadena de caracteres en blanco
            elif stringVacio(newCat):
                typeErr="empty"
                st.session_state.success = False

            else: #Condición de exíto::
                st.session_state.success = True

    with col2:  #Lista de las categorías ya en la DB
        with st.popover("Lista de categorías"):
            st.write(catList)

    #Visibilidad habilitada solo si se la al botón:
    if (st.session_state.visibility ):

        if not(st.session_state.success): #No se efectuó con éxito la operación
            st.warning("No se pudo agregar la categoría")
            
            #Tipo de mensaje de error:
            match typeErr:
                case "empty":
                    html("<script>alert('Categoría no puede ser una cadena de caracteres vacios')</script>")

                case "cat": #Mostrar con una alerta de JS
                    html("<script>alert('Categoría ya en uso')</script>")
                    
        else:   #La categoría ingresada SÍ es valida:
            if st.button("✅ Confimar cambio"): #Botón de confirmación
                try:
                    o.agregarCategoria(newCat)
                except:
                    st.error("No se pudo añadir la nueva categoría")
                else:
                    st.success("Categoría añadida con exito")
                    time.sleep(tiempo_reset)
                    try:
                        st.session_state.visibility = False
                    except:
                        pass
                    else:
                        st.rerun()

#ELIMINAR CATEGORÍA:                        
#----------------------------------------------------------------------------------
else:
    catList = o.read_catList() #Lista con todas las categorías.
    catList.remove("Otro")     #La categoría "Otro" siempre se debe dejar

    #Seleccionar la categoría que se piensa eliminar
    oldCat  = st.selectbox("Seleccione una categoría", options=catList)

    col1, col2 = st.columns(2)

    with col2: #Confirmación para eliminar categoría:
        conf = st.checkbox("Estoy seguro que quiero eliminar esta categoría")

    with col1:
        if st.button("🗑️ Eliminar", disabled=not(conf)):
            try:
                o.eliminarCategoriaXDesc(oldCat)
            except:
                st.error("No se pudo eliminar la categoría ingresada")
            else:
                exitoEliminacion = True

if exitoEliminacion:
    st.info("Se logró eliminar la categoría con éxito")
    time.sleep(tiempo_reset)
    st.rerun()