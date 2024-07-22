import base64
import datetime
import os
import numpy as np
from acuerdos.acuerdo import Acuerdo
from acuerdos.schema import creacion_datos_acuerdo
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import date

#Creacion del objeto acuerdo y su dataframe respectivo

st.set_page_config(page_title="Caida Cartera | RSI", page_icon="./rsi.ico", layout="centered", initial_sidebar_state="auto", menu_items=None)

dataframe=creacion_datos_acuerdo("x")


def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    bin_str = "data:image/png;base64," + base64.b64encode(data).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
with open("./style.css") as f:
    st.markdown(f'<style>{f.read()}<style>',unsafe_allow_html=True)

#URL para la llamada desde la API
DATE_COLUMN = 'tti'
#URL Para la conexión y visualización del entorno virtual
DATA_URL = ('https://localhost:8080/streamlit/Principal')

# Cargar la imagen
image_fondo = Image.open('./image2.jpg')

page_bg_img = '''
<style>
body {
background-image: url({image_fondo});
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

add_bg_from_local('./image2.jpg')

# URL de la imagen
image_url="./Image.jpg"
# Mostrar la imagen
image = st.image(image_url)

st.title('Caída Cartera')

tipo_de_interes = st.sidebar.selectbox("Tipo de Interes", ["Fijo","Variable","Mixto"])
tti=dataframe['TTI'][0]
fecha_de_ultima_renovacion = datetime.date(2024,1,2)                     
frecuencia_de_proxima_revision = datetime.date(2024,3,2)  
curva_euribor = dataframe['Curva del eurivor'][0] 
spread_curva_de_referencia= dataframe['Spread Curva de referencia'][0]       
tipo_de_interes_deudor = dataframe['Tipo de interes deudor'][0]
anualidad=100
if tipo_de_interes=="Fijo":

    metodo_de_amortizacion = st.sidebar.selectbox("Metodo de amortización", ["Cuota Constante","Principal Constante","Bullet/Ballon"])                                    
    saldo_pendiente = st.sidebar.number_input('saldo pendiente por amortizar',value=dataframe['Saldo pendiente por amortizar'][0])                             
    tasa_de_interes = st.sidebar.number_input("Tasa de Interes",value=dataframe['Tasa de interes'][0])                      
    saldo_de_capital_inicial = st.sidebar.number_input('saldo de capital inicial',value=dataframe['Saldo de capital inicial'][0])                                  
    fecha_de_constitucion = st.sidebar.date_input('fecha de constitucion')                                        
    fecha_de_pago_de_ultima_cuota = st.sidebar.date_input('fecha de pago de ultima cuota')                             
    fecha_de_vencimiento = st.sidebar.date_input('fecha de vencimiento')                                    
    frecuencia_de_pago = st.sidebar.number_input('frecuencia de pago', min_value=0, step=1,value=1)  #a                                      
    unidad_frecuencia_pago = st.sidebar.text_input('unidad frecuencia pago',value="M")                                    
  

elif tipo_de_interes=="Variable":

    metodo_de_amortizacion = st.sidebar.selectbox("Metodo de amortización", ["Cuota Constante","Principal Constante","Bullet/Ballon"])                                    
    tti = st.sidebar.number_input('TTI',value=dataframe['TTI'][0])
    saldo_pendiente = st.sidebar.number_input('saldo pendiente por amortizar',value=dataframe['Saldo pendiente por amortizar'][0])                             
    tasa_de_interes = st.sidebar.number_input("Tasa de Interes",value=dataframe['Tasa de interes'][0])                                        
    saldo_de_capital_inicial = st.sidebar.number_input('saldo de capital inicial',value=dataframe['Saldo de capital inicial'][0])                                  
    fecha_de_constitucion = st.sidebar.date_input('fecha de constitucion')                                        
    fecha_de_pago_de_ultima_cuota = st.sidebar.date_input('fecha de pago de ultima cuota')                             
    fecha_de_vencimiento = st.sidebar.date_input('fecha de vencimiento')                                    
    frecuencia_de_pago = st.sidebar.number_input('frecuencia de pago', min_value=0, step=1,value=1)  #a                                      
    unidad_frecuencia_pago = st.sidebar.text_input('unidad frecuencia pago',value="M")                                    
    fecha_de_ultima_renovacion = st.sidebar.date_input('fecha de ultima renovacion', key='fecha_renovacion')                                
    frecuencia_de_proxima_revision = st.sidebar.date_input('frecuencia de proxima revision')                            
    spread_curva_de_referencia = st.sidebar.number_input('spread de curva de referencia',value=dataframe['Spread Curva de referencia'][0])                                                                           
    tipo_de_interes_deudor = st.sidebar.number_input('tipo de interes deudor',value=dataframe['Tipo de interes deudor'][0])         
    curva_euribor = st.sidebar.number_input('curva euribor',value=dataframe['Curva del eurivor'][0])     

elif tipo_de_interes=="Mixto":

    metodo_de_amortizacion = st.sidebar.selectbox("Metodo de amortización", ["Cuota Constante","Principal Constante","Bullet/Ballon"])                                    
    tti = st.sidebar.number_input('TTI',value=dataframe['TTI'][0])
    saldo_pendiente = st.sidebar.number_input('saldo pendiente por amortizar',value=dataframe['Saldo pendiente por amortizar'][0])                             
    tasa_de_interes = st.sidebar.number_input("Tasa de Interes",value=dataframe['Tasa de interes'][0])         
    saldo_de_capital_inicial = st.sidebar.number_input('saldo de capital inicial',value=dataframe['Saldo de capital inicial'][0])                                  
    fecha_de_constitucion = st.sidebar.date_input('fecha de constitucion')                                        
    fecha_de_pago_de_ultima_cuota = st.sidebar.date_input('fecha de pago de ultima cuota')                             
    fecha_de_vencimiento = st.sidebar.date_input('fecha de vencimiento')                                    
    frecuencia_de_pago = st.sidebar.number_input('frecuencia de pago', min_value=0, step=1,value=1)  #a                                      
    unidad_frecuencia_pago = st.sidebar.text_input('unidad frecuencia pago',value="M")                                    
    fecha_de_ultima_renovacion = st.sidebar.date_input('fecha de ultima renovacion', key='fecha_renovacion')                                
    frecuencia_de_proxima_revision = st.sidebar.date_input('frecuencia de proxima revision')                            
    spread_curva_de_referencia = st.sidebar.number_input('spread de curva de referencia',value=dataframe['Spread Curva de referencia'][0])                                                                           
    tipo_de_interes_deudor = st.sidebar.number_input('tipo de interes deudor',value=dataframe['Tipo de interes deudor'][0])         
    curva_euribor = st.sidebar.number_input('curva euribor',value=dataframe['Curva del eurivor'][0])      
print(type(fecha_de_constitucion))




if metodo_de_amortizacion=="Principal Constante":
    anualidad = st.sidebar.number_input('anualidad', min_value=0, step=1)                            


if isinstance(fecha_de_constitucion, date):
    fecha_de_constitucion = fecha_de_constitucion.strftime("%d-%m-%Y")
else:
    fecha_de_constitucion = "Fecha no válida"
    

if isinstance(fecha_de_ultima_renovacion, date):
    fecha_de_ultima_renovacion = fecha_de_ultima_renovacion.strftime("%d-%m-%Y")
else:
    fecha_de_ultima_renovacion = "Fecha no válida"
    
    
if isinstance(fecha_de_pago_de_ultima_cuota, date):
    fecha_de_pago_de_ultima_cuota = fecha_de_pago_de_ultima_cuota.strftime("%d-%m-%Y")
else:
    fecha_de_pago_de_ultima_cuota = "Fecha no válida"
    
if isinstance(fecha_de_vencimiento, date):
    fecha_de_vencimiento = fecha_de_vencimiento.strftime("%d-%m-%Y")
else:
    fecha_de_vencimiento = "Fecha no válida"

if isinstance(frecuencia_de_proxima_revision, date):
    frecuencia_de_proxima_revision = frecuencia_de_proxima_revision.strftime("%d-%m-%Y")
else:
    frecuencia_de_proxima_revision = "Fecha no válida"
# if frecuencia_de_proxima_revision<=fecha_de_ultima_renovacion:
#     frecuencia_de_proxima_revision = "La Fecha del proximo reprecio no puede ser menor o igual a la del proximo"

if curva_euribor==None:
    curva_euribor=111

nueva_fila = {
                    "tti":tti,
                    "saldo_pendiente":float(saldo_pendiente),  # type: ignore
                    "tasa_de_interes":float(tasa_de_interes), # type: ignore
                    "anualidad":float(anualidad),
                    "metodo_de_amortizacion":metodo_de_amortizacion,
                    "tipo_de_interes":tipo_de_interes,
                    "saldo_de_capital_inicial":float(saldo_de_capital_inicial), # type: ignore
                    "fecha_de_constitucion":fecha_de_constitucion,
                    "fecha_de_pago_de_ultima_cuota":fecha_de_pago_de_ultima_cuota,
                    "fecha_de_vencimiento":fecha_de_vencimiento,
                    "frecuencia_de_pago":float(frecuencia_de_pago),
                    "unidad_frecuencia_pago":unidad_frecuencia_pago,
                    "fecha_de_ultima_renovacion":fecha_de_ultima_renovacion,
                    "frecuencia_de_proxima_revision":frecuencia_de_proxima_revision,
                    "spread_curva_de_referencia":float(spread_curva_de_referencia), # type: ignore
                    "tipo_de_interes_deudor":float(tipo_de_interes_deudor),   # type: ignore
                    "Curva_euribor":curva_euribor
                    }

dataframe_labels=["tti","saldo_pendiente",
"tasa_de_interes",
"anualidad",
"metodo_de_amortizacion",
"tipo_de_interes",
"saldo_de_capital_inicial",
"fecha_de_constitucion",
"fecha_de_pago_de_ultima_cuota",
"fecha_de_vencimiento",
"frecuencia_de_pago",
"unidad_frecuencia_pago",
"fecha_de_ultima_renovacion",
"frecuencia_de_proxima_revision",
"spread_curva_de_referencia",
"tasa_cliente",
"tipo_de_interes_deudor" ,
"Curva_euribor"
]




# Botón para agregar los datos al DataFrame
if st.sidebar.button('Visualizar Cuotas'):
    if metodo_de_amortizacion=="Principal Constante" and anualidad<=0:
        anualidad = "La anualidad no puede ser menor o igual a 0 en el metodo Principal Constante"
    #Se le asigna la estructura al dataframe
    dataframe=pd.DataFrame(columns=dataframe_labels)
    dataframe = pd.concat([dataframe,pd.DataFrame([nueva_fila])], ignore_index=True)

    print(type(dataframe['fecha_de_constitucion']))
    # Crear un diccionario con los datos ingresados
    data = {
        'tti':[tti],
        'saldo_pendiente' : [saldo_pendiente],
        'tasa_de_interes' : [tasa_de_interes],
        'anualidad':[int(anualidad)],
        'metodo_de_amortizacion' : [metodo_de_amortizacion],
        'tipo_de_interes' : [tipo_de_interes],
        'saldo_de_capital_inicial' : [saldo_de_capital_inicial],
        'fecha_de_constitucion' : [fecha_de_constitucion],
        'fecha_de_pago_de_ultima_cuota' : [fecha_de_pago_de_ultima_cuota],
        'fecha_de_vencimiento' : [fecha_de_vencimiento],
        'frecuencia_de_pago' : [frecuencia_de_pago],
        'unidad_frecuencia_pago' : [unidad_frecuencia_pago],
        'fecha_de_ultima_renovacion' : [fecha_de_ultima_renovacion],
        'frecuencia_de_proxima_revision' : [frecuencia_de_proxima_revision],
        'spread_curva_de_referencia' : [spread_curva_de_referencia],
        'tipo_de_interes_deudor' : [tipo_de_interes_deudor],
        "Curva_euribor":[curva_euribor]
    }

    # Crear un DataFrame con los datos
    dataf_entrada = pd.DataFrame(data)

    acuerdo_objeto=Acuerdo(dataf_entrada['saldo_pendiente'],
                            dataf_entrada['tasa_de_interes'],  #Esto se puede reemplazar por MI_PORC_I_D_UP_P (EN EL EXCEL) que es la tasa de interes deudor
                            dataf_entrada['metodo_de_amortizacion'],
                            dataf_entrada['tipo_de_interes'],
                            dataf_entrada["saldo_de_capital_inicial"],
                            dataf_entrada['fecha_de_constitucion'],
                            dataf_entrada['fecha_de_pago_de_ultima_cuota'],
                            dataf_entrada['fecha_de_vencimiento'],
                            dataf_entrada['frecuencia_de_pago'],
                            dataf_entrada['unidad_frecuencia_pago'],
                            dataf_entrada['fecha_de_ultima_renovacion'],
                            dataf_entrada['frecuencia_de_proxima_revision'],
                            dataf_entrada['spread_curva_de_referencia'],
                            dataf_entrada["tipo_de_interes_deudor"],
                            dataf_entrada['Curva_euribor'])
    # Mostrar el DataFrame
    st.write('Tabla de entrada:')
    st.write(dataf_entrada)

    if 'dataf_entrada' not in st.session_state:
        st.session_state.dataf_entrada = dataf_entrada
    else:
        st.session_state.dataf_entrada = pd.concat([st.session_state.dataf_entrada, dataf_entrada], ignore_index=True)
        
    dataframe_salida= acuerdo_objeto.calculo_acuerdo(dataf_entrada['tti'],dataf_entrada["anualidad"])

    # Mostrar el DataFrame completo
    st.write('Tabla de Salida:')
    #Tratamiento del Dataframe para que no salgan columnas adicionales vacias
    dataframe_salida.replace("", np.nan, inplace=True)
    dataframe_salida = dataframe_salida.dropna(axis=1, how='all')
    #Mostramos el Dataframe por pantalla
    st.write(dataframe_salida)







