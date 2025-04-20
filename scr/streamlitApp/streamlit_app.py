import streamlit as st


st.set_page_config(
    page_title="Mises' App",
    page_icon="https://media3.giphy.com/media/njON3jEmTYHEfRbfsk/giphy.gif?cid=6c09b9525bbr07s93freua26rpxlfwwmw2iacpfdyl4owu54&ep=v1_stickers_search&rid=giphy.gif&ct=s",
    layout="wide",
    initial_sidebar_state="expanded",
)


#Function to Load CSS from the assets folder
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path  = "C:\\Users\\gabri\\OneDrive\\Documentos\\MisesApp\\scr\\assets\\styles.css"
load_css(css_path)



sidebar_logo    = "https://images.icon-icons.com/2069/PNG/512/graphic_coins_finance_icon_125518.png"
main_body_logo  = "https://media3.giphy.com/media/njON3jEmTYHEfRbfsk/giphy.gif?cid=6c09b9525bbr07s93freua26rpxlfwwmw2iacpfdyl4owu54&ep=v1_stickers_search&rid=giphy.gif&ct=s"

st.logo(sidebar_logo, icon_image=main_body_logo)

pages = {
    "ℹ️ Información": [
        st.Page("P10_dash.py", title="Dashboard"),
        st.Page("P11_cat.py", title ="Analísis por categoría"),

    ],
    "⚙️ Configuración": [
        st.Page("P01_upload.py", title="Cargar nueva información"),
        st.Page("P02_AddCat.py", title="Categorías"),
        st.Page("P03_ChangeCats.py", title="Agrupar descripciones"),



    ]

}

pg = st.navigation(pages)
pg.run()
# run ./scr/streamlitApp/streamlit_app.py [ARGUMENTS]