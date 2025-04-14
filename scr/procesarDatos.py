import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
import psycopg2
import toml
import io
import csv
import seaborn as sns
import matplotlib.pyplot as plt

f_path  = "C:\\Users\\gabri\\OneDrive\\Documentos\\MisesApp\\scr\\misTransacciones.csv"

stringVacio = lambda string: string.strip() == ""

def no_esta_contenido_en_lista(cadena, lista):
    return not(all(cadena not in item for item in lista))

class leerDatos:
    def __init__(self, selectMode=True, filePath=f_path, stringData=""):
        self.filePath   = filePath
        self.StringData = stringData

        self.rawData = []
        self.df = None
        if selectMode:  #Si selectMode es verdadero: Sacar información de un archivo csv
            self.leerArchivo()
        else:           #Si selectMode es falso: Sacar información de un string
            self.leerString()

        self.lector2RawData()
        self.crearDf()

    def leerArchivo(self):
        with open(self.filePath, newline='', encoding='latin1') as archivo:
            lector = csv.reader(archivo)
            lector = list(lector)
        self.lector= lector
        return lector
    
    def leerString(self):
        # Convertimos el string a un objeto tipo archivo
        archivo_simulado = io.StringIO(self.StringData)

        # Leemos usando el módulo csv
        lector = csv.reader(archivo_simulado)
        # Convertimos a lista
        lector = list(lector)
        self.lector= lector
        return lector

    def lector2RawData(self):
        infoTransacciones=[]
        beginTrans=False

        for fila in self.lector:

            if beginTrans and (fila==[]):
                beginTrans = False

            if beginTrans:
                infoTransacciones.append(fila)
            
            if (len(fila)==1):
                if  fila[0]=='Detalle de Estado Bancario':
                    beginTrans=True
    
        self.rawData = infoTransacciones
        return infoTransacciones

    def crearDf(self):
        infoTransacciones=pd.DataFrame(self.rawData)
        #Renombrar columnas:
        infoTransacciones.columns = ["Fechas", "Referencia", "Código", "Descripición", "Débito", "Crédito", "Balance"]
        infoTransacciones = infoTransacciones.drop(index=0) #Eliminar primera fila

        #Convertir columnas a tipo de variable necesario:
        infoTransacciones["Crédito"]    = infoTransacciones["Crédito"].astype(float)
        infoTransacciones["Débito"]     = infoTransacciones["Débito"].astype(float)
        infoTransacciones["Balance"]    = infoTransacciones["Balance"].astype(float)

        infoTransacciones["Fechas"]     =  pd.to_datetime(infoTransacciones['Fechas'], format='%d/%m/%Y')

        #Crear columna de aporte neto:
        infoTransacciones["Aporte neto"] = infoTransacciones["Crédito"]- infoTransacciones["Débito"]
        
        self.df = infoTransacciones
        return infoTransacciones

    #DB:
    #%%
    def readDataFromSecrets(self, secretsPath):

        # Cargar el archivo .toml
        with open(secretsPath, 'r') as f:
            secrets = toml.load(f)
        secrets_db=secrets["connections"]["postgresql"]
        return secrets_db
    
    def write_histFromDB(self, my_df, secretsPath = "C:\\Users\\gabri\\.streamlit\\secrets.toml"):
        secrets_db= self.readDataFromSecrets(secretsPath)
        engine = create_engine(f'postgresql://{secrets_db["username"]}:{secrets_db["password"]}@{secrets_db["host"]}:{secrets_db["port"]}/{secrets_db["database"]}')

        my_df.to_sql('historial', engine, if_exists='append', index=False)
    
    def writ2DB(self):
        upDf=self.df.copy().drop(columns=["Aporte neto"])
        upDf.columns =["fechas","referencia","codigo","descripcion","debito","credito","balance"]
        self.write_histFromDB(upDf)
    #%%

class datos(leerDatos):
    def __init__(self, selectMode=True, filePath=f_path, stringData="", readFromDB=True):
        super().__init__(selectMode, filePath, stringData)
        self.connect2DB()
        self.read_histFromDB(redfineDf=readFromDB)
        self.read_catFromDB()

    def encontrarIDCategoria(self, descripcion):
        df_des = self.read_catTableDesc().copy()
        indx_categoriaAEliminar =int(df_des.query("descripcion ==@descripcion")["id"])
        return indx_categoriaAEliminar
    
    #TODO: Decorador de df:
    def decDf(self):
        pass
    #DB:
    #%%
    
    def crearConexion(self, secretsPath = "C:\\Users\\gabri\\.streamlit\\secrets.toml"):
        secrets_db= self.readDataFromSecrets(secretsPath)

        # Configuración de conexión
        conn = psycopg2.connect(
            host        = secrets_db["host"],
            port        = secrets_db["port"],
            database    = secrets_db["database"],
            user        = secrets_db["username"],
            password    = secrets_db["password"]
        )
        return conn
    

    def write_hist(self, params):
        
        conn = self.crearConexion()
        
        # Crear un cursor
        cur = conn.cursor()

        # Llamar al procedimiento almacenado con el input
        # Consulta SQL
        insert_query = "CALL insertar_movimiento(%s, %s, %s, %s, %s, %s, %s);"
        # Llamar al procedimiento almacenado con el input
        cur.execute(insert_query, (
            params["p_fechas"],                 # p_fechas
            params["p_referencia"],             # p_referencia
            params["p_codigo"],                 # p_codigo
            params["p_descripcion"],            # p_descripcion
            params["p_debito"],                 # p_debito
            params["p_credito"],                # p_credito
            params["p_balance"]                 # p_balance
            
            ,))
        
        
        # Guardar los cambios
        conn.commit()

        # Cerrar cursor y conexión
        cur.close()
        conn.close()
    
    def write_histConTipo(self, p_fechas, p_referencia, p_codigo, p_descripcion, p_monto, p_balance, tipo_monto=False):
        #Si tipo_monto es True: La transacción es un Débito / Si tipo_monto es False: La transacción es un Crédito
        p_debito    = p_monto if tipo_monto else 0
        p_credito   = p_monto if not(tipo_monto) else 0
        params={
            "p_fechas"      : str(p_fechas),            
            "p_referencia"  : str(p_referencia),            
            "p_codigo"      : str(p_codigo),            
            "p_descripcion" : str(p_descripcion),            
            "p_debito"      : float(p_debito),            
            "p_credito"     : float(p_credito),            
            "p_balance"     : float(p_balance)             
        }
        self.write_hist(params)
    
    def eliminarCategoriaXID(self, id):
        
        conn = self.crearConexion()
        
        # Crear un cursor
        cur = conn.cursor()

        # Consulta SQL
        insert_query = "CALL eliminar_categoria(%s);"

        # Llamar al procedimiento almacenado con el input
        cur.execute(insert_query, (id,))

        # Guardar los cambios
        conn.commit()

        # Cerrar cursor y conexión
        cur.close()
        conn.close()
    
    def eliminarCategoriaXDesc(self, desc):
        id = self.encontrarIDCategoria(desc)
        self.eliminarCategoriaXID(id)
    
    def agregarCategoria(self, descripcion):
        conn = self.crearConexion()
        
        # Crear un cursor
        cur = conn.cursor()

        # Consulta SQL
        insert_query = "CALL insertar_descripcioncategorias(%s);"

        # Llamar al procedimiento almacenado con el input
        cur.execute(insert_query, (descripcion,))

        # Guardar los cambios
        conn.commit()

        # Cerrar cursor y conexión
        cur.close()
        conn.close()

    def connect2DB(self):
        self.conn = st.connection("postgresql", type="sql")

    def read_histFromDB(self, redfineDf=True):
        hist_df =   self.conn.query('SELECT * FROM historial;', ttl="0m")
        if redfineDf:
            hist_df.set_index("id", inplace=True)
            hist_df.columns=["Fechas", "Referencia", "Código", "Descripcion", "Débito", "Crédito", "Balance"]
            hist_df["Aporte neto"] = hist_df["Crédito"]-hist_df["Débito"]

            self.df = hist_df
        return hist_df
    
    def read_catTable(self):
        return self.conn.query("SELECT * FROM categorias;", ttl="0m")

    def read_catTableDesc(self):
        return self.conn.query("SELECT * FROM categorias_descripcion;", ttl="0m")


    def read_catFromDB(self):
        categorias_full  = self.conn.query('SELECT * FROM obtener_categorias_descripcion();', ttl="0m")
        categorias_full.columns =["Descripción", "Categoría"]
        return categorias_full
    
    def read_catList(self):
        lista_categorias  = self.conn.query('SELECT *  FROM categorias_descripcion;', ttl="0m")["descripcion"].to_list()
        return lista_categorias

    #%%

    def nuevasCategorias(self):
        Descripciones_DB        = self.read_catList()
        Descripciones_Actuales  = pd.unique(self.df["Descripición"].to_list())

        DescripcionesNuevas = [i for i in Descripciones_Actuales if i not in Descripciones_DB]
        return DescripcionesNuevas
    
    #DATA ANALYSIS:
    def colData(self, col, toArr=False):
    
        q = "Débito !=0" if (col == "Débito") else "Crédito !=0"
        r   = self.df[[col]].query(q)
        if toArr:
            r=r[col].to_list()
        return r

    def colStat(self, col):
        return self.colData(col).describe()

    def styledDF(self, df=None):
        if df is None:
            df=self.df

        df_styled = df.style.map(lambda val: 'background-color: lightgreen; color: black; font-weight:bold' if val>=0 else 'background-color: red; font-weight:bold', subset=['Aporte neto'])
        return df_styled
    
    def gananciasPerdidas(self, df=None):
        if df is None:
            df = self.df
        ganacias_d    = float(df["Crédito"].sum())
        gastos_d      = float(df["Débito"].sum())

        return {"ganancias":ganacias_d, "gastos":gastos_d}
    

    #GRÁFICOS:
    #%%---------------------------------------------------------------------------------------------------------------------------
    def boxPlot_GastosYGanancias(self):
        cred=self.colData("Crédito", toArr=True)
        deb=self.colData("Débito", toArr=True)

        # Crear DataFrame con etiquetas
        df = pd.DataFrame({
            'Valores': cred + deb,
            'Grupo': ['Crédito'] * len(cred) + ['Débito'] * len(deb)
        })

        # Crear box plot
        fig = px.box(df, x='Grupo', y='Valores', points='all', title='Box Plot de Grupo Crédito vs Débito')

        return fig
    def disp_GastosYGanancias(self, col, nbins=10):
        data = self.colData(col, toArr=True)
        fig = px.histogram(data, nbins=10, title='Histograma de Datos')

        fig.update_layout(
            xaxis_title=col,
            yaxis_title='Frecuencia',
            bargap=0.1,
            plot_bgcolor='white'
        )
        return fig
    
    def graph_gananciasPerdidas(self, df=None):
        if df is None:
            df = self.df
        ganacias_d    = float(df["Crédito"].sum())
        gastos_d      = float(df["Débito"].sum())


        # Crear gráfico de barras
        fig = go.Figure(data=[
            go.Bar(name='Gastos', x=['Gastos'], y=[gastos_d]),
            go.Bar(name='Ingresos', x=['Ingresos'], y=[ganacias_d])
        ])

        # Personalizar
        fig.update_layout(
            title='Comparación de Gastos e Ingresos',
            xaxis_title='Categoría',
            yaxis_title='Valor',
            barmode='group'
        )

        return fig
    
    def graph_BalanceXTime(self):
        # Crear gráfico de línea
        fig = px.line(self.df, x='Fechas', y='Balance', title='Balance a lo largo del tiempo')
        # Línea punteada, sin puntos, con grosor mayor y área sombreada
        fig.update_traces(
            fill='tozeroy',
            line=dict(
                color='royalblue',
                width=4,
                dash='dash'  # punteada
            ),
            mode='lines'  # solo la línea, sin markers/puntos
        )

        # Fondo rayado horizontal y vertical (cuadrícula completa)
        fig.update_layout(
            yaxis_title='Balance',
            xaxis_title='Fecha',
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgrey',
                gridwidth=1
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgrey',
                gridwidth=1
            )
        )

        return fig
    #%%---------------------------------------------------------------------------------------------------------------------------
    
