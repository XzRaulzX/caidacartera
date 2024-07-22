"""
En este fichero se establecera la conexion con la base de datos para poder operar con ella
"""
import pandas as pd
import cx_Oracle
import os
# from dotenv import load_dotenv
def creacion_datos_acuerdo(cursor):
    
    dataframe=pd.read_csv("./data/ejemploAcuerdos1.csv",encoding="ISO-8859-1",sep=";")

    # sql=""
    # cursor.execute(sql)
    # euribor = cursor.fetchall()
    # columnas = [desc[0] for desc in cursor.description]
    # dataframe = pd.DataFrame(euribor, columns=columnas)
    # obejetoCaida=cuadros_amortizacion(dataframe['Saldo pendiente por amortizar'],dataframe['Tasa de interes']/100,dataframe['Fecha de vencimiento'],[2000,3000])

    # dataframe["Fecha de vencimiento"] = pd.to_datetime(dataframe["Fecha de vencimiento"]).dt.strftime('%d-%m-%Y')
    # dataframe["Fecha de constitucion"] = pd.to_datetime(dataframe["Fecha de constitucion"]).dt.strftime('%d-%m-%Y')
    # dataframe["Fecha de pago de ultima cuota"] = pd.to_datetime(dataframe["Fecha de pago de ultima cuota"]).dt.strftime('%d-%m-%Y')


    return dataframe



def creacion_datos_euribor(cursor):
    
    # df_euribor=pd.read_csv("./data/euribor.csv",encoding="ISO-8859-1",sep=",")
    df_euribor=pd.read_csv("./data/euriborP.csv",encoding="ISO-8859-1",sep=",")
    
    # sql=""
    # cursor.execute(sql)
    # euribor = cursor.fetchall()
    # columnas = [desc[0] for desc in cursor.description]
    # df_euribor = pd.DataFrame(euribor, columns=columnas)

    return df_euribor

#Creamos la conexion con la base de datos
def conexion():
    connection_string="""{user}/{password}@{service_name}""".format(
            user=os.getenv('user'),
            password=os.getenv('password'),
            service_name=os.getenv('service_name')
        )

    conn = cx_Oracle.connect(connection_string)
    cursor = conn.cursor()
    df_euribor=creacion_datos_euribor(cursor)
    df_acuerdos=creacion_datos_acuerdo(cursor)
    
    return df_euribor,df_acuerdos 

try:
    # print(cx_Oracle.clientversion())
    # conexion()
    print("Conexion Realizada con Exito")
except cx_Oracle.Error as error:
    print(error)