from streamlit_option_menu import option_menu
from procesarDatos import *
import time


o = datos()
exito = False

cat_df = o.read_catFromDB()
lista_descripciones = cat_df["Descripción"].tolist()
lista_categorias    = o.read_catList()

st.html("<h1 style='color:white;padding-left:20px;background: linear-gradient(to right, #8b0000, #ff0000, #ffa07a); border-radius:10px 50px 50px 10px'>Editar descripciones <h1>")

with st.sidebar:
    selected = option_menu("Opciones", ["Configurar varias descripciones", 'Configurar descripción'],
                            
        icons=['bookmarks-fill', 'bookmark-fill'], menu_icon="gear", default_index=0)

if selected == "Configurar varias descripciones":

    edited_df = st.data_editor(cat_df,
    column_config={
        "Categoría":st.column_config.SelectboxColumn(
            "Categoría",
            help="¿Qué clase de gasto fue este?",
            options=lista_categorias,
        ),},
    disabled=["Descripción"],
    )
    
    col1, col2 = st.columns(2)
    with col2:
        conf= st.checkbox("Confirmar cambio")
    with col1:
        if st.button("💾 Realizar cambio", disabled=not(conf)):
            try:
                with st.spinner():
                    o.setCatXDesc_DF(edited_df)
            except:
                st.error("Hubo un error")
            else:
                exito= True

else:
    select_desc = st.selectbox("Descripción a editar", options=lista_descripciones)
    new_cat = st.selectbox("Categoría a establecer", options=lista_categorias)
    st.write(f"'{select_desc}'")
    col1, col2 = st.columns(2)
    with col2:
        conf= st.checkbox("Confirmar cambio")
    with col1:
        if st.button("💾 Realizar cambio", disabled=not(conf)):
            try:
                o.setCatXDesc(select_desc, new_cat)
            except:
                st.error("Hubo un error")
            else:
                exito= True
if exito:
    st.success("Cambio realizado con éxito")
    time.sleep(3)
    st.rerun()