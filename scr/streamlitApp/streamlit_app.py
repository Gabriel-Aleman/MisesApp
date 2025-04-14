import streamlit as st
st.set_page_config(
    page_title="Mises' App",
    page_icon="https://media3.giphy.com/media/njON3jEmTYHEfRbfsk/giphy.gif?cid=6c09b9525bbr07s93freua26rpxlfwwmw2iacpfdyl4owu54&ep=v1_stickers_search&rid=giphy.gif&ct=s",
    layout="wide",
    initial_sidebar_state="expanded",
)



sidebar_logo    = "https://images.icon-icons.com/2069/PNG/512/graphic_coins_finance_icon_125518.png"
main_body_logo  = "https://media3.giphy.com/media/njON3jEmTYHEfRbfsk/giphy.gif?cid=6c09b9525bbr07s93freua26rpxlfwwmw2iacpfdyl4owu54&ep=v1_stickers_search&rid=giphy.gif&ct=s"

st.logo(sidebar_logo, icon_image=main_body_logo)

pages = {
    "⚙️ Configuración": [
        st.Page("P01_upload.py", title="Subir nuevos datos desde CSV"),
        st.Page("P04_AddHistMan.py", title="Subir nuevo dato manualmente"),
        st.Page("P02_AddCat.py", title="Agregar categoría"),
        st.Page("P03_delCat.py", title="Eliminar categoría"),


    ],
    "ℹ️ Mi información": [
        st.Page("P10_dash.py", title="Learn about us"),
    ],
}

pg = st.navigation(pages)
pg.run()
# run ./scr/streamlitApp/streamlit_app.py [ARGUMENTS]