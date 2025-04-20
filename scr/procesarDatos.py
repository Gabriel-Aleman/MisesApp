from datetime import datetime, timedelta
from sqlalchemy import create_engine
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import pandas as pd
import psycopg2
import toml
import csv
import io


# VARIABLES GLOBALES:
#-----------------------------------------------------------------------------------------------------------
f_path  = "C:\\Users\\gabri\\OneDrive\\Documentos\\MisesApp\\scr\\misTransacciones.csv"
colores_plotly= [
    "#636EFA",  # Azul Plotly
    "#EF553B",  # Rojo coral
    "#00CC96",  # Verde menta
    "#AB63FA",  # Violeta
    "#FFA15A",  # Naranja suave
    "#19D3F3",  # Celeste
    "#FF6692",  # Rosa
    "#B6E880",  # Verde lima claro
    "#FF97FF",  # Rosa claro
    "#FECB52"   # Amarillo dorado
]

# Fecha actual
hoy = datetime.today()
hoy = hoy.replace(hour=0, minute=0, second=0, microsecond=0)

#   FUNCIONES:
#-----------------------------------------------------------------------------------------------------------
#%%
def stringVacio(texto):
    return texto.strip() == ''

"""Función para obtener el primer y último día de la semana anterior"""
def semanaAnterior(fechaActual=hoy):
    lunes_esta_semana = fechaActual - timedelta(days=fechaActual.weekday())
    inicio_semana_anterior = lunes_esta_semana - timedelta(days=7)
    fin_semana_anterior = inicio_semana_anterior + timedelta(days=6)
    fin_semana_anterior = fin_semana_anterior.replace(hour=23, minute=59, second=59)
    return inicio_semana_anterior, fin_semana_anterior

"""Función para obtener el primer y último día del mes anterior"""
def mesAnterior(fechaActual=hoy):
    primer_dia_mes_actual = fechaActual.replace(day=1)
    fin_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
    inicio_mes_anterior = fin_mes_anterior.replace(day=1)
    fin_mes_anterior = fin_mes_anterior.replace(hour=23, minute=59, second=59)
    return inicio_mes_anterior, fin_mes_anterior

#Decoradores
'''
A todo método que recibe un df como parámetro, si este no le es dado
Qué entonces como valor default tome el atributo de la clase.
'''
def df_dec(func):
    def wrap(self, df = None):
        if df is None:
            df = self.df
        return func(self, df)
    return wrap

'''
A todo método que recibe un df y una de sus columnas como parámetros, si este último no le es dado
Qué entonces, si el df tiene una sola columna, tome esta por default.
'''
def col_dec(func):
    def wrap(self, df, col=None):
        if (col is None) and (len(df.columns) == 1):
            col = df.columns[0]
        return func(self, df, col)
    
    return wrap
#%%

#   CLASES:
#-----------------------------------------------------------------------------------------------------------
class leerDatos:
    def __init__(self, selectMode=True, filePath=f_path, stringData="", Idle_funcs = True):
        self.filePath   = filePath      #Ruta de archivo csv con la información
        self.StringData = stringData    #Texto con la información

        self.rawData = []               #Información convertida a un array
        self.df = None                  #Información convertida a un df

        if Idle_funcs: #Funciones para inicializar el objeto
            
            if selectMode:  #Si selectMode es verdadero: Sacar información de un archivo csv
                self.leerArchivo()
            else:           #Si selectMode es falso: Sacar información de un string
                self.leerString()

            self.lector2RawData()
            self.crearDf()

    '''Método que devuelve la información financiera a partir del archivo dado'''
    def leerArchivo(self):
        with open(self.filePath, newline='', encoding='latin1') as archivo:
            lector = csv.reader(archivo)
            lector = list(lector)
        self.lector= lector
        return lector
    
    '''Método que devuelve la información financiera a partir de un string'''
    def leerString(self):
        # Convertimos el string a un objeto tipo archivo
        archivo_simulado = io.StringIO(self.StringData)

        # Leemos usando el módulo csv
        lector = csv.reader(archivo_simulado)
        # Convertimos a lista
        lector = list(lector)
        self.lector= lector
        return lector

    '''Método que toma la información del archivo o string y lo convierte en el formato raw data'''
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

    '''Método para crear un df a partir de los datos en bruto'''
    def crearDf(self):
        infoTransacciones=pd.DataFrame(self.rawData)
        #Renombrar columnas:
        infoTransacciones.columns = ["Fechas", "Referencia", "Código", "Descripción", "Débito", "Crédito", "Balance"]
        infoTransacciones = infoTransacciones.drop(index=0) #Eliminar primera fila

        #Convertir columnas a tipo de variable necesario:
        infoTransacciones["Crédito"]        = infoTransacciones["Crédito"].astype(float)
        infoTransacciones["Débito"]         = infoTransacciones["Débito"].astype(float)
        infoTransacciones["Balance"]        = infoTransacciones["Balance"].astype(float)
        infoTransacciones["Descripción"]    = infoTransacciones["Descripción"].astype(str).str.strip()

        infoTransacciones["Fechas"]     =  pd.to_datetime(infoTransacciones['Fechas'], format='%d/%m/%Y')
        
        self.df = infoTransacciones
        return infoTransacciones

    #DB:
    #%%
    '''Método para obtener la información de la DB'''
    def readDataFromSecrets(self, secretsPath):
        # Cargar el archivo .toml
        with open(secretsPath, 'r') as f:
            secrets = toml.load(f)
        secrets_db=secrets["connections"]["postgresql"]
        return secrets_db
    
    '''Método para escribir la información de df a la base de datos'''
    def write_hist2DB(self,  secretsPath = "C:\\Users\\gabri\\.streamlit\\secrets.toml"):
        secrets_db= self.readDataFromSecrets(secretsPath)
        engine = create_engine(f'postgresql://{secrets_db["username"]}:{secrets_db["password"]}@{secrets_db["host"]}:{secrets_db["port"]}/{secrets_db["database"]}')
        my_df =self.df.copy()
        my_df.columns = ["fechas", "referencia", "codigo", "descripcion", "debito", "credito", "balance"]
        my_df.to_sql('historial', con=engine, if_exists='append', index=False)
    

    def writ2DB(self):
        upDf=self.df.copy().drop(columns=["Aporte neto"])
        upDf.columns =["fechas","referencia","codigo","descripcion","debito","credito","balance"]
        self.write_histFromDB(upDf)


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
    

    #DB:
    #%%
    '''Método para crear una conexión con la base de datos'''
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
    
    '''Método para insertar un único elmento al historial'''
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
    
    '''Método para insertar un único elmento al historial con valor de crédito o débito'''
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
    
    '''Método eliminar una categoría de la DB por medio de su id'''
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

    '''Método para eliminar una categoría de la DB por medio de su descripción'''
    def eliminarCategoriaXDesc(self, desc):
        id = self.encontrarIDCategoria(desc)
        self.eliminarCategoriaXID(id)

    '''Método para editar la categoría de una descripción'''
    def setCatXDesc(self, descProd, descCat):
        id = self.encontrarIDCategoria(descCat)
        conn = self.crearConexion()
        print(id)
        print(descProd)
        # Crear un cursor
        cur = conn.cursor()

        update_query = "UPDATE categorias SET categoria = %s WHERE TRIM(descripcion) = %s;"

        cur.execute(update_query, (id, descProd))

        # Guardar los cambios
        conn.commit()

        # Cerrar cursor y conexión
        cur.close()
        conn.close()

    '''Método para editar la categoría de todas las descripciones'''
    def setCatXDesc_DF(self, df):
        for index, fila in df.iterrows():
            descripcionActual    = fila["Descripción"]
            categoriaActual      = fila["Categoría"]
            self.setCatXDesc(descripcionActual, categoriaActual)

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

    def agregarDescripcion(self, descripcion, cat=1):
        conn = self.crearConexion()
        # Crear un cursor
        cur = conn.cursor()
        # Consulta SQL
        insert_query = "CALL insertar_categorias(%s, %s);"

        # Llamar al procedimiento almacenado con el input
        cur.execute(insert_query, (descripcion, cat))

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
            hist_df.columns = ["Fechas", "Referencia", "Código", "Descripción", "Débito", "Crédito", "Balance"]
            hist_df["Aporte neto"] = hist_df["Crédito"]-hist_df["Débito"]
            hist_df["Fechas"] = pd.to_datetime(hist_df['Fechas'])
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
    
    '''Método que retorna un df con todas las categorías de la DB'''
    def read_catList(self):
        lista_categorias  = self.conn.query('SELECT *  FROM categorias_descripcion;', ttl="0m")["descripcion"].to_list()
        return lista_categorias

    #%%
    '''Método que retorna una lista con las nuevas descripciones del df, que no están en la db'''
    def nuevasCategorias(self):
        descripciones_actuales  = self.conn.query('SELECT *  FROM categorias;', ttl="0m")["descripcion"].to_list()
        descripciones_nuevas    = list(pd.unique(self.df.query("Débito != 0")["Descripción"]))
        descripciones_nuevas    =  [x for x in descripciones_nuevas if x not in descripciones_actuales]
        return descripciones_nuevas
    
    #DATA ANALYSIS:
    '''Método que retorna un df con todas las filas correspondientes a débitos con sus 
    respectivas categorías'''
    def dataFrame_Categorias(self):
        d1=self.df
        d2=self.read_catFromDB()
        df_cat = pd.merge(d1, d2, how='left', on='Descripción')
        df_cat = df_cat.query("Débito !=0 ")
        df_cat.drop(columns=["Crédito","Balance","Aporte neto"], inplace=True)
        return df_cat
    
    '''Método que devuelve las estadísticas de los gastos agrupados x Categoría'''
    def dataFrame_Categorias_Stad(self, df=None):
        if df is None:
            df = self.dataFrame_Categorias()
            
        df_f_stad = df.groupby("Categoría")["Débito"].agg([
            'sum',       # Suma total
            'mean',      # Promedio
            'count',     # Cantidad de registros
            'min',       # Mínimo
            'max',       # Máximo
            'median',    # Mediana
            'std',       # Desviación estándar
            'var'        # Varianza
        ]).reset_index()
    
        # Renombrar columnas a español
        df_f_stad.columns = [
            "Categoría", 
            "Suma", 
            "Promedio", 
            "Cantidad", 
            "Mínimo", 
            "Máximo", 
            "Mediana", 
            "Desviación estándar", 
            "Varianza"
        ]
        return df_f_stad
    '''Método que devuelve el último valor de balance en el registro'''
    @df_dec
    def ultimoValorBalance(self, df):
        return df.sort_values(by="Fechas",ascending=False).iloc[0]["Balance"]

    '''Método que devuelve la información de credito o débito según se le especifique'''
    def colData(self, df=None, col="", toArr=False, addDates=False):
        if df is None:
            df = self.df
        columnas = [col] if not(addDates) else["Fechas", col]

        q = "Débito !=0" if (col == "Débito") else "Crédito !=0"
        r   = df[columnas].query(q)
        if toArr:
            r=r[col].to_list()
        return r

    '''Método que devuelve las estádisticas de una columna según se le especifique'''
    @col_dec
    def colStat(self, df, col):

        estad = df[[col]].describe()
        estad = estad.iloc[1:]
        estad.index = ["Prom", "STD", "min", "25%", "50%", "75%", "max"]
        return estad
    
    '''Método que colorea la columna de aporte neto en verde o rojo, según si aporte fue positivo o
    negativo respectivamente.'''
    @df_dec
    def styledDF(self, df):
        df_styled = df.style.map(lambda val: 'background-color: lightgreen; color: black; font-weight:bold' if val>=0 else 'background-color: red; font-weight:bold', subset=['Aporte neto'])
        return df_styled
    
    '''Método que retorna la suma de las ganacias y consumo en total'''
    @df_dec
    def gananciasPerdidas(self, df):
        ganacias_d    = float(df["Crédito"].sum())
        gastos_d      = float(df["Débito"].sum())

        return {"ganancias":ganacias_d, "gastos":gastos_d}
    
    '''Método que retorna un data frame con datos de los días de pago'''
    @df_dec
    def datosDePago(self, df):
        return df.query("Código == ' PE'")

    #GRÁFICOS:
    #%%---------------------------------------------------------------------------------------------------------------------------
    def boxPlot_Graph(self, df, col, my_color=colores_plotly[0]):
        fig = px.box(df,  y=col, points="all",  title=col.capitalize()+" - boxplot")
        fig.update_layout(
            xaxis_title="",
            template="plotly_white",
            showlegend=False,
            title_font=dict(size=20),
            margin=dict(l=150, r=150, t=60, b=40)
        )
        fig.update_traces(line=dict(color=my_color),  marker=dict(color=my_color, size=10))  # Cambia el color de la línea
        return fig
    
    def Hist_Graph(self, df, col, my_color=colores_plotly[0], bins=10):
        fig = px.histogram(df, x=col, nbins=bins, title='Distribución de '+col)
        fig.update_layout(xaxis_title='Monto', yaxis_title='Frecuencia')
        fig.update_traces(marker_color = my_color)
        return fig
    
    def violinPlot_Graph(self, df, col, my_color=colores_plotly[0]):
        fig = px.violin(
            df,
            y=col,
            points="all",     # Muestra todos los puntos
            box=True,         # Agrega boxplot dentro del violín
            title=col.capitalize() + " - violin plot"
        )
        fig.update_layout(
            xaxis_title="",
            template="plotly_white",
            showlegend=False,
            title_font=dict(size=20),
            margin=dict(l=150, r=150, t=60, b=40)
        )
        fig.update_traces(
            line_color=my_color,                 # Color del contorno del violín
            marker=dict(color=my_color, size=10) # Color de los puntos
        )
        return fig

    def barPlot_Graph(self, df, col, my_color='Viridis'):
        if df is None:
            df = self.df
        fig = px.bar(df, x='Fechas', y=col, color=col,
                    color_continuous_scale=my_color,  # Cambia la paleta de colores,
                    title=col.capitalize()+" x Fecha")
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
    
    @df_dec
    def graph_BalanceXTime(self, df):
        # Crear gráfico de línea
        fig = px.line(df, x='Fechas', y='Balance', title='Balance a lo largo del tiempo')
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

    @df_dec
    def graph_IntXTime(self, df):
        intereses_cod = " 3O"
        df_int = df.query("Código == @intereses_cod")
        fig = px.line(df_int, x="Fechas", y="Crédito", title='Interes en función del tiempo', markers=True)
        fig.update_traces(
             fill='tonexty',  # Rellenar hasta y=0,
            line=dict(
                color='red',
            ),
        )
        fig.update_layout(
            yaxis_title='Intereses',

            xaxis=dict(
                showgrid=True,
                gridwidth=1
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1
            )
        )

        return fig
    #%%---------------------------------------------------------------------------------------------------------------------------
    
