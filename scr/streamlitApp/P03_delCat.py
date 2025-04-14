from streamlit.components.v1 import html
from procesarDatos import *
import time
o = datos()
catList=o.read_catList()
catList.remove("Otro")
oldCat=st.selectbox("Seleccione una categoría", options=catList)

col1, col2 = st.columns(2)

with col2:
    conf = st.checkbox("Estoy seguro que quiero eliminar esta categoría")

with col1:
    if st.button("🗑️ Eliminar", disabled=not(conf)):
        try:
            o.eliminarCategoriaXDesc(oldCat)
        except:
            st.error("No se pudo eliminar la categoría ingresada")
        else:
            st.info("Se logró eliminar la categoría con éxito")
            time.sleep(2)
            st.rerun()