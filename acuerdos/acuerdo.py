"""
En este archivo creamos el objeto Acuerdo y todos los metodos genericos necesarios para
el calculo de las distintas variables necesarias para la salida de los acuerdos
"""
import datetime
from datetime import date, timedelta
import pandas as pd
import os
import numpy as np
from acuerdos.schema import creacion_datos_euribor
class Acuerdo:
    """
    Esta clase sera el objeto generico de los acuerdos, 
    donde se aplicaran todos los 
    metodos genericos para los acuerdos
    """
    def __init__(self,capital_pendiente,interes,metodo,tipo_interes,saldo_inicial,fecha_constitucion,
                 fecha_ultima_cuota,fecha_vencimiento,frec_pago,unidad_frec_pago,fecha_ult_reno,fecha_prox_rev,
                 spread,tasa_interes_deudor,curva_euribor):
        self.interes=interes/12
        self.metodo=metodo.str.lower()
        self.acuerdo=tipo_interes.str.lower()
        self.saldo_inicial=capital_pendiente
        self.capital_prestado=saldo_inicial
        self.saldo_final=0
        self.tasa_cliente=tasa_interes_deudor/12
        self.tasa_interes_deudor=tasa_interes_deudor
        self.spread=spread
        self.fecha_constitucion=fecha_constitucion
        self.fecha_ultima_cuota=fecha_ultima_cuota
        self.fecha_vencimiento=fecha_vencimiento
        self.fecha_ult_reno=fecha_ult_reno
        self.fecha_prox_rev=fecha_prox_rev
        self.frecuencia_pago=frec_pago
        self.curva=curva_euribor
        self.unidad_frec_pago=unidad_frec_pago.str.upper()
        #variables auxiliares
        self.fecha_actual = datetime.datetime.now()
        self.cap_amort_anterior=0
        #Si el estado de mixto es 1 significa que se comportara como un acuerdo variable
        self.fecha_reprecio_variable=0
        self.estado_mixto=0
        #Creamos un dataframe con los valores del euribor
        self.dataf_euribor=creacion_datos_euribor("x")
        #Se crea la estructura de columnas que tendra nuestro dataframe
        dataframe_labels=["Pago de Cuota","Estado Reprecio","Ultimo Reprecio",
                          "Proximo Reprecio","Fecha vencimiento","Tipo de acuerdo","Metodo de Amortizacion",
                          "Tasa Interes","Interes","Cuota",
                          "Amortizacion en Periodo","Capital Amortizado",
                          "Saldo Inicial","Capital Promedio",
                          "Capital Promedio*","Saldo Final","TT",
                          "ajuste neto recurso","ingresos financieros",
                          "Frecuencia De Pago","Unidad Frecuencia De Pago","Reprecio"]
        #Se le asigna la estructura al dataframe
        self.dataframe_salida=pd.DataFrame(columns=dataframe_labels)

    #Calculamos el capital promedio a partir de las variables con las que se construye un objeto de tipo acuerdo 
    def saldo_capital_promedio(self,saldo_inicial,fecha_constitucion,fecha_cuota,saldo_final,estado_reprecio):
        """
        Con este metodo calcularemos el saldo
        promedio a partir del saldo inicial, el saldo final
        D1, D2 y los dias totales que haya el 
        mes de la ejecucion del programa
        """
        def calcular_d1_d2(fecha_constitucion, fecha_cuota):
            """
            Con esta funcion calcularemos las
            variables D1,D2 y los dias totales del mes, 
            necesarias para el calculo del 
            saldo promedio a partir de la fecha de constitucion 
            de la cuota y la fecha de pago de la ultima cuota existente
            """
            #Convertimos las series en objetos Datatime para manejar las fechas y operar con ellas
            fecha_constitucion = pd.to_datetime(fecha_constitucion, format='%d-%m-%Y')
            fecha_cuota = pd.to_datetime(fecha_cuota, format='%d-%m-%Y')
            ultimo_dia_mes = (fecha_cuota.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + 
                              datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            dias_mes = ultimo_dia_mes.day
            # Cálculo de d1 y d2 para aplicar en la formula de saldo promedio
            if fecha_cuota.day==1:
                d1=fecha_cuota.day
            else:
                d1 = fecha_cuota.day-1
            d2 = (ultimo_dia_mes-fecha_cuota).days
            return d1, d2, dias_mes

        #Aplicamos la formula para conseguir el capital promedio en cada celda del DataFrame
        medio_reprecio=0
        saldo_promedio=0
        d1, d2, dias_mes = calcular_d1_d2(fecha_constitucion, fecha_cuota)
        #Añadimos a la lista el saldo inicial como saldo promedio en caso de que no exista cuota pagada el mes que se ejecuta el programa  
        if estado_reprecio.lower()=="x":
            #Comprobar si hay que restarle 1 a los dias totales del mes
            medio_reprecio=(d2*saldo_final)/dias_mes
            
        else:
            medio_reprecio=0
    
        if d2>=dias_mes:
            saldo_promedio=saldo_inicial  
        else:
                #Calculamos el saldo promedio siguiendo las formulas y lo añadimos a la lista
                if estado_reprecio.lower()=="x":
                    saldo_promedio = (saldo_inicial * d1) / dias_mes
                else:
                    saldo_promedio = ((saldo_inicial * d1) + (saldo_final * d2)) / (dias_mes-1)
        return saldo_promedio,medio_reprecio


    #Declaracion de los metodos que comprobaran el estado del reprecio 
    def reprecio(self,fecha_prox_rev,fecha_ult_reno):
        """
        Calculamos el reprecio a partir de la diferencia entre la fecha de la proxima revision y la ultima
        """
        fecha_prox_rev=pd.to_datetime(fecha_prox_rev, format='%d-%m-%Y')
        fecha_ult_reno=pd.to_datetime(fecha_ult_reno, format='%d-%m-%Y')
        frecuencia_reprecio= abs((fecha_prox_rev.year - fecha_ult_reno.year) * 12 + (fecha_prox_rev.month - fecha_ult_reno.month))
        return frecuencia_reprecio
    #Se puede borrar
    def fechas_reprecio(self,fecha_prox_rev,frecuencia_reprecio):
        """
        Con este metodo generaremos todas las fechas que tengan reprecio a lo largo de 26 proyecciones
        """
        
        fecha_prox_rev=pd.to_datetime(fecha_prox_rev, format='%d-%m-%Y')
        lista_fech_reprecio=[fecha_prox_rev]
        for i in range(26//frecuencia_reprecio):
            mes_fech_reprecio=lista_fech_reprecio[i].month+frecuencia_reprecio
            if mes_fech_reprecio>12:
                año_fech_reprecio=lista_fech_reprecio[i].year+1
                mes_fech_reprecio=mes_fech_reprecio-12
                fecha_rep=datetime.date(año_fech_reprecio,mes_fech_reprecio,lista_fech_reprecio[i].day)
                lista_fech_reprecio.append(fecha_rep)
                
            else:
                fecha_rep=datetime.date(lista_fech_reprecio[i].year,mes_fech_reprecio,lista_fech_reprecio[i].day)
                lista_fech_reprecio.append(fecha_rep)
        return lista_fech_reprecio

    def estado_revision_mixto(self,fecha_cuota_ori,ciclo,frecuencia_reprecio_meses=12):
        """
        Con este metodo comprobaremos si existe un reprecio en el mes proyectado o no
        """
        
        estado_revision_mixto = ""
        #Tratamiento con las fechas para que no se generen fechas incorrectas
        fecha_mixto_mes=fecha_cuota_ori.month
        fecha_mixto_year=fecha_cuota_ori.year
        fecha_revision_tipo=pd.to_datetime(self.fecha_ult_reno[ciclo], format='%d-%m-%Y')
        if fecha_mixto_mes==0:
            fecha_mixto_mes=12
            fecha_mixto_year-=1
        fecha_mixto=datetime.date(fecha_mixto_year,fecha_mixto_mes,fecha_cuota_ori.day)
        #Comprobacion de evento de cambio de tipo
        if pd.Timestamp(fecha_mixto)>=fecha_revision_tipo:
            estado_revision_mixto = "X"
            # En caso de que haya reprecio asignamos la proxima fecha del reprecio y la ultima fecha del reprecio 
            # haciendo un control de fechas para no generar fechas incorrectas
            # self.fecha_ult_reno[ciclo]=self.fecha_prox_rev[ciclo]
            prox_reprecio=pd.to_datetime(self.fecha_ult_reno[ciclo],format="%d-%m-%Y")
            mes_prox_reprecio=prox_reprecio.month+frecuencia_reprecio_meses
            año_prox_reprecio=prox_reprecio.year
            if mes_prox_reprecio>12:
                mes_prox_reprecio=mes_prox_reprecio-12
                año_prox_reprecio+=1
            self.fecha_ult_reno[ciclo]=datetime.date(año_prox_reprecio,mes_prox_reprecio,prox_reprecio.day).strftime("%d-%m-%Y")
      
        return estado_revision_mixto


    # def estado_reprecio(self,fecha_cuota,frecuencia_reprecio_meses,ciclo):
    #     """
    #     Con este metodo comprobaremos si existe un reprecio en el mes proyectado o no
    #     """
        
    #     estado_reprecio = ""
    #     fecha_cuota = pd.to_datetime(fecha_cuota, format='%d-%m-%Y')
    #     self.fecha_prox_rev[ciclo]= pd.to_datetime(self.fecha_prox_rev[ciclo], format='%d-%m-%Y')
    #     # Convertir lista_fecha a Timestamps si no lo está ya
       
    #     if self.fecha_prox_rev[ciclo]<=fecha_cuota:
    #         while self.fecha_prox_rev[ciclo]<fecha_cuota:
    #             fec_prox_reprecio=pd.to_datetime(self.fecha_prox_rev[ciclo],format="%d-%m-%Y")
    #             mes_prox_reprecio=fec_prox_reprecio.month+frecuencia_reprecio_meses
    #             año_prox_reprecio=fec_prox_reprecio.year
    #             if mes_prox_reprecio>12:
    #                 mes_prox_reprecio=mes_prox_reprecio-12
    #                 año_prox_reprecio+=1
    #             self.fecha_prox_rev[ciclo]=pd.Timestamp(datetime.date(año_prox_reprecio,mes_prox_reprecio,fec_prox_reprecio.day))
           
    #         self.fecha_ult_reno[ciclo]=fecha_cuota.strftime("%d-%m-%Y")
    #         estado_reprecio = "X"
    #     diferencia_dias=(self.fecha_prox_rev[ciclo] - fecha_cuota).days

    #     if diferencia_dias<=30 and diferencia_dias>=0 or diferencia_dias==0:
    #             mes_fech_reprecio=fecha_cuota.month
    #             if mes_fech_reprecio>12:
    #                 año_fech_reprecio=fecha_cuota.year+1
    #                 mes_fech_reprecio=mes_fech_reprecio-12
    #                 fecha_rep=pd.Timestamp(datetime.date(año_fech_reprecio,mes_fech_reprecio,fecha_cuota.day))
    #                 self.fecha_reprecio_variable=fecha_rep
                    
    #             else:
    #                 fecha_rep=pd.Timestamp(datetime.date(fecha_cuota.year,mes_fech_reprecio,fecha_cuota.day))
    #                 self.fecha_reprecio_variable=fecha_rep

    #     if self.fecha_reprecio_variable!=0:
    #         if pd.Timestamp(fecha_cuota)>=pd.Timestamp(self.fecha_reprecio_variable):
    #             print(fecha_cuota)
    #             estado_reprecio = "X"
    #             # En caso de que haya reprecio asignamos la proxima fecha del reprecio y la ultima fecha del reprecio 
    #             # haciendo un control de fechas para no generar fechas incorrectas
    #             self.fecha_ult_reno[ciclo]=fecha_cuota.strftime("%d-%m-%Y")
    #             prox_reprecio=pd.to_datetime(self.fecha_ult_reno[ciclo],format="%d-%m-%Y")
    #             mes_prox_reprecio=prox_reprecio.month+frecuencia_reprecio_meses
    #             año_prox_reprecio=prox_reprecio.year
    #             if mes_prox_reprecio>12:
    #                 mes_prox_reprecio=mes_prox_reprecio-12
    #                 año_prox_reprecio+=1
    #             self.fecha_prox_rev[ciclo]=datetime.date(año_prox_reprecio,mes_prox_reprecio,fecha_cuota.day).strftime("%d-%m-%Y")
    #             self.fecha_reprecio_variable=datetime.date(año_prox_reprecio,mes_prox_reprecio,fecha_cuota.day)
    #     return estado_reprecio

    def estado_reprecio(self,lista_fecha,fecha_cuota,frecuencia_reprecio_meses,ciclo):
        """
        Con este metodo comprobaremos si existe un reprecio en el mes proyectado o no
        """
        
        estado_reprecio = ""
        fecha_cuota = pd.Timestamp(fecha_cuota)
        
        # Convertir lista_fecha a Timestamps si no lo está ya
        lista_fecha = [pd.Timestamp(fecha) for fecha in lista_fecha]

        for fecha_reprecio in lista_fecha:
            # Calcular la diferencia en meses entre la fecha de reprecio y la fecha de cuota
            diferencia_meses = (fecha_cuota.year - fecha_reprecio.year) * 12 + fecha_cuota.month - fecha_reprecio.month
            
            # Verificar si la diferencia de meses es múltiplo de la frecuencia de reprecio 
            if diferencia_meses % frecuencia_reprecio_meses == 0 and fecha_cuota >= fecha_reprecio:
                estado_reprecio = "X"
                # En caso de que haya reprecio asignamos la proxima fecha del reprecio y la ultima fecha del reprecio 
                # haciendo un control de fechas para no generar fechas incorrectas
                self.fecha_ult_reno[ciclo]=fecha_cuota.strftime("%d-%m-%Y")
                prox_reprecio=pd.to_datetime(self.fecha_ult_reno[ciclo],format="%d-%m-%Y")
                mes_prox_reprecio=prox_reprecio.month+frecuencia_reprecio_meses
                año_prox_reprecio=prox_reprecio.year
                if mes_prox_reprecio>12:
                    mes_prox_reprecio=mes_prox_reprecio-12
                    año_prox_reprecio+=1
                self.fecha_prox_rev[ciclo]=datetime.date(año_prox_reprecio,mes_prox_reprecio,prox_reprecio.day).strftime("%d-%m-%Y")
                # break

        return estado_reprecio
    
    def recalculo_tasa_cliente(self,tasa_cliente,curva_euribor,spread,fecha_cuota,tipo):
        
        def interes_euribor(fecha_cuota,curva_euribor,tipo):
            if tipo=="variable":
                df_euribor_filtrado = self.dataf_euribor[
                                                            (pd.to_datetime(self.dataf_euribor['FECHA_OPRCN']).dt.month == fecha_cuota.month) & 
                                                            (pd.to_datetime(self.dataf_euribor['FECHA_OPRCN']).dt.year == fecha_cuota.year) & 
                                                            (self.dataf_euribor['COD_FAM_REF_INT_FORWARD'] == int(curva_euribor))
                                                        ] 
                tipo_interes_curva=df_euribor_filtrado["IG_TIPO_INT"].to_list()
                return tipo_interes_curva[0]
            elif tipo=="mixto":
                df_euribor_filtrado = self.dataf_euribor[
                                                            (pd.to_datetime(self.dataf_euribor['FECHA_OPRCN']).dt.month == fecha_cuota.month) & 
                                                            (pd.to_datetime(self.dataf_euribor['FECHA_OPRCN']).dt.year == fecha_cuota.year) & 
                                                            (self.dataf_euribor['COD_FAM_REF_INT_FORWARD'] == int(curva_euribor)) & 
                                                            (self.dataf_euribor['IG_PERIODO'] == 12)
                                                        ] 
                tipo_interes_curva=df_euribor_filtrado["IG_TIPO_INT"].to_list()
                return tipo_interes_curva[0]
            
        # tasa_cliente=spread+
        euribor_interes=interes_euribor(fecha_cuota,curva_euribor,tipo)

        tasa_cliente=(spread+euribor_interes)/12
        # tasa_cliente=(tasa_deudor+euribor_interes)/12
        return tasa_cliente

    def recalculo_tasa_transferencia(self,tasa_transferencia_interna,tasa_interes_deudor,tasa_cliente):
        tasa_interna=tasa_cliente-((tasa_interes_deudor/12)-tasa_transferencia_interna)
        return tasa_interna

    #Funciones para los calculos de las variables de Acuerdo
    def ajuste_neto_recursos(self,saldo_promedio,tasa_transferencia_interna):
        """
        Calculamos el ajuste neto por recursos a partir del 
        saldo promedio y la TTI
        """
        ajuste_neto=saldo_promedio*(tasa_transferencia_interna*(1/12)*0.01)
        return ajuste_neto
    
    def ajuste_neto_recursos_reprecio(self,saldo_promedio,saldo_promedio_reprecio,tasa_transferencia_interna,tasa_recalculada):
        """
        Calculamos el ajuste neto por recursos a partir del 
        saldo promedio y la TTI
        """
        
        ajuste_neto=(saldo_promedio*(tasa_transferencia_interna/12)+saldo_promedio_reprecio*(tasa_recalculada/12))*0.01
        return ajuste_neto

    def ingreso_interes_real(self,saldo_promedio,tasa_cliente):
        """
        Calculamos el ingreso por interes real a partir de 
        la tasa de cliente y el saldo promedio
        """
        ingreso_interes=+saldo_promedio*(tasa_cliente/12)*0.01
        return ingreso_interes
    def ingreso_interes_real_reprecio(self,saldo_promedio,saldo_promedio_reprecio,tasa_interes_deudor):
        """
        Calculamos el ingreso por interes real a partir de 
        la tasa de cliente y el saldo promedio
        """

        
        ingreso_interes=+(saldo_promedio*(tasa_interes_deudor/12)+saldo_promedio_reprecio*(tasa_interes_deudor/12))*0.01
        return ingreso_interes
    
    def capital_amortizado_periodo(self,saldo_fin_mes,saldo_inicio_mes):
        
        """
        Calculamos la reduccion de la deuda capital restando el 
        Saldo fin de mes - el Saldo inicio de mes
        """
        amortizacion_periodo=saldo_inicio_mes-saldo_fin_mes
        return amortizacion_periodo
    

    #Aqui comienzan las funciones para el calculo del cuadro de amortizacion

    #Metodo Cuota Constante
    def anualidad_constante(self,capital_prestado,tipo_interes_anual,numero_periodos):
        """
        Con esta funcion calcularemos la anualidad dentro del  
        cuadro de amortizacion a partir de 3 variables: Capital Prestado,
        Tipo de interes anual del prestamo y Numero de periodos
        """
        #En caso de acuerdo variable la formula que se aplica es la siguiente:
        #CapitalPrestado*((tasa_deudor/12)*0,01/(1-(1+(tasa_deudor/12)*0,01)^(-n_cuota)));
        
        anualidad=capital_prestado*(tipo_interes_anual*0.01/(1-(1+tipo_interes_anual*0.01)**-numero_periodos))

        return round(anualidad,7)

    
    def interes_periodo(self,capital_pendiente,tasa):
        """
        Esta funcion calcula el Interes a partir de 2 variables: 
        Capital Amortizado y Tipo de interes anual del prestamo
        Tambien se aplicara al acuerdo variable a partir de la tasa 
        de cliente y el capital pendiente
        """
        interes=(capital_pendiente*tasa)*0.01
        return round(interes,8)
    
    def amortizacion_capital(self,anualidad,interes):
        """
        Esta funcion calcula la Amortizacion Capital a partir de 
        2 variables: Anualidad e Interes
        """
        amortizacion=anualidad-interes
        return round(amortizacion,7)


    def capital_amortizado(self,amortizacion_capital,cap_amort_anterior):
        """
        Esta funcion calcula el Capital Amortizado a 
        partir de dos variables 
        Amortizacion Capital y Año
        """
        capital_amortizado=amortizacion_capital+cap_amort_anterior
        self.cap_amort_anterior=capital_amortizado
        return round(capital_amortizado,6)


    def capital_pendiente(self,capital_prestado,capital_amortizado_periodo):
        """
        Esta funcion calcula el Capital Pendiente 
        a partir del capital vivo en el momento
        """
        pendiente=capital_prestado-capital_amortizado_periodo
        return round(pendiente,5)


    #Metodo Principal Constante
    def anualidad_principal_constante(self,capital_amortizado_constante,interes):
        """
        Con esta funcion calcularemos la anualidad dentro 
        del cuadro de amortizacion mediante 
        el metodo Principal Constante a partir de 
        2 variables: El capital amortizado (Ck) y el interes
        """
        anualidad=capital_amortizado_constante+interes
        return anualidad

    #Metodo bullet/ballon
    def anualidad_bullet(self,capital_prestado,tipo_interes_anual,year,n_periodos):

        """
        Con esta funcion calcularemos la anualidad
        dentro del cuadro de amortizacion mediante el 
        metodo Bullet/Ballon a partir de 4 variables: 
        Capital Prestado, Tipo de interes anual del prestamo, 
        Numero de periodos y el periodo actual
        """
        if year>=n_periodos:
            anualidad=capital_prestado+(capital_prestado*(tipo_interes_anual)*0.01)
        else:
            anualidad=capital_prestado*(tipo_interes_anual*0.01)
        return anualidad
    
    def tasa_transferencia_proyectada(self,tasa_cliente_presente,tasa_cliente_proyectada,tasa_transferencia_presente):
        """
        Calculamos la Tasa de transferencia proyectada mediante 
        la metodologia spread fijo
        """
        spread=tasa_cliente_presente-tasa_transferencia_presente
        t_transferencia_proyectada=tasa_cliente_proyectada-spread
        return t_transferencia_proyectada
    
    def calculo_acuerdo(self,tasa_transferencia_interna,a):    
        """
        Con este metodo crearemos y calcularemos el conjunto de 
        datos y se los asignaremos al dataframe de salida 
        """
        #Con esta variable el programa sabra en que serie de datos esta posicionado
        #exactamente para realizar los calculos necesarios
        n_ciclo=0
        frecuencia_reprecio=1
        tasa_transferencia_interna_base=tasa_transferencia_interna
        #Recorremos los tipos de acuerdo para comprobar de que tipo es el acuerdo que estamos
        #tratando actualmente, dependiendo de su tipo se aplican unas funciones u otras
        
        for tipo,a in zip(self.acuerdo,a) :
            #Tratamiento para fechas reprecio (Actualizacion mantener vigilado)
            fecha_prox_rev=pd.to_datetime(self.fecha_prox_rev[n_ciclo], format='%d-%m-%Y')
            fecha_ult_reno=pd.to_datetime(self.fecha_ult_reno[n_ciclo], format='%d-%m-%Y')
            dia_cuota=pd.to_datetime(self.fecha_ultima_cuota[n_ciclo], format='%d-%m-%Y')

            self.fecha_prox_rev[n_ciclo]=fecha_prox_rev.replace(day=dia_cuota.day).strftime("%d-%m-%Y")
            self.fecha_ult_reno[n_ciclo]=fecha_ult_reno.replace(day=dia_cuota.day).strftime("%d-%m-%Y")

            #Declaramos las variables necesarias para iniciar el calculo de los acuerdos en cada periodo
            self.cap_amort_anterior=self.capital_prestado[n_ciclo]-self.saldo_inicial[n_ciclo]
            proyecciones=(24-self.fecha_actual.month)

            if proyecciones == 12:
                proyecciones=24

            elif proyecciones >12 and proyecciones<15:
                proyecciones=(12-self.fecha_actual.month)+24    
            
            year=1
            mes_actual = self.fecha_actual.month
            año_actual = self.fecha_actual.year
            bucle=True
            fecha = datetime.datetime.strptime(self.fecha_vencimiento[n_ciclo], '%d-%m-%Y')
            if tipo=="variable" or tipo=="mixto":
                frecuencia_reprecio=self.reprecio(self.fecha_prox_rev[n_ciclo],self.fecha_ult_reno[n_ciclo])
                lista_fecha_reprecio=self.fechas_reprecio(self.fecha_prox_rev[n_ciclo],frecuencia_reprecio)
            #Se calcula la diferencia de meses entre el mes actual 
            #al ejecutar el programa y la fecha de vencimiento
            constitucion=pd.to_datetime(self.fecha_constitucion[n_ciclo], format="%d-%m-%Y")
            vencimiento = (fecha.year - constitucion.year) * 12 + (fecha.month - constitucion.month)
            
            #Hacemos el tratamiento de errores y manipulamos los datos que llegan
            #si en un futuro se implementan los pagos Anuales como unidad de pago
            #el programa hara el tratamiento respectivo para poder operar con esa unidad
            if self.frecuencia_pago[n_ciclo]<=0:
                print("Frecuencia de pago incorrecta")
                n_ciclo+=1
                continue
            elif self.unidad_frec_pago[n_ciclo]=="A" or self.unidad_frec_pago[n_ciclo]=="Y":
                #Preguntar a Borja si implementamos el anual o lo dejamos únicamente en mensual como está ahora
                self.frecuencia_pago[n_ciclo]=self.frecuencia_pago[n_ciclo]*12
                #Formateamos la fecha con 12 mensualidades para hacerlo anual
                self.unidad_frec_pago[n_ciclo]="M"

            #Comprobamos que la cuota no haya vencido, en el caso
            #de que no haya vencido dividimos por la frecuencia de pago
            #para proyectar los meses a pagar
            if vencimiento<=0:
                print("Ya ha vencido la cuota")
                n_ciclo+=1
                continue
            else:
                vencimiento=vencimiento/self.frecuencia_pago[n_ciclo]
                proyecciones=proyecciones/self.frecuencia_pago[n_ciclo]
            
            mes=self.fecha_actual.month+frecuencia_reprecio
            año=self.fecha_actual.year
            if mes>12:
                año+=1
                mes=mes-12
            # fecha_reprecio=datetime.date(año,mes,self.fecha_actual.day)

            while(bucle):
                proyecciones-=1
                # Suma la frecuencia de pago a la fecha actual para obtener el mes de pago

                mes_actual = mes_actual + self.frecuencia_pago[n_ciclo]
                # Ajustar el año si el nuevo mes excede diciembre
                if mes_actual > 12:
                    mes_actual -= 12
                    año_actual += 1

                #Formateamos la fecha de la ultima cuota pagada para poder manipularla
                fecha_ultima_cuota = pd.to_datetime(self.fecha_ultima_cuota[n_ciclo], format='%d-%m-%Y')
                fecha_cuota=datetime.date(año_actual,mes_actual,fecha_ultima_cuota.day).strftime("%d-%m-%Y")
                estado_reprecio=""
                    
                if tipo=="irregular":

                    saldo_promedio,medio_reprecio=self.saldo_capital_promedio(self.saldo_inicial[n_ciclo],self.fecha_constitucion,
                                                               fecha_cuota,self.saldo_final,estado_reprecio)
               
                    
                    ajuste_neto=self.ajuste_neto_recursos(saldo_promedio,
                                                        tasa_transferencia_interna_base[n_ciclo])
                    
                    ingreso_real=self.ingreso_interes_real(saldo_promedio,
                                                            self.tasa_cliente[n_ciclo])
                    
                    # amortizado_periodo=self.capital_amortizado_periodo(self.saldo_final[n_ciclo],
                    #                                                     self.saldo_inicial[n_ciclo])
                    
                    #Falta inicializar el saldo final y 
                    #el Inicio al tener los cuadros de amortizacion de IRIS
                    #Insertamos en el Dataframe los datos calculados en este periodo como una nueva fila
                    nueva_fila = { 
                    "Pago de Cuota": fecha_cuota,
                    "Estado Reprecio":estado_reprecio,
                    "Fecha vencimiento":self.fecha_vencimiento[n_ciclo],
                    "Tipo de acuerdo":tipo,
                    "Metodo de Amortizacion":self.metodo[n_ciclo],
                    "Tasa Interes":self.interes[n_ciclo],
                    "Interes": None,
                    "Cuota": None,
                    "Amortizacion en Periodo": None,
                    "Capital Amortizado": None,
                    "Saldo Inicial": self.saldo_inicial[n_ciclo],
                    "Capital Promedio": saldo_promedio,
                    "Capital Promedio*": medio_reprecio,
                    "Saldo Final": self.saldo_final,
                    "ajuste neto recurso": ajuste_neto,
                    "ingresos financieros": ingreso_real,
                    "Frecuencia De Pago":self.frecuencia_pago[n_ciclo], 
                    "Unidad Frecuencia De Pago":self.unidad_frec_pago[n_ciclo]
                    # "Reprecio":frecuencia_reprecio
                    }

                elif tipo=="fijo":
                    
                    # co_restado=self.capital_prestado[n_ciclo]-self.cap_amort_anterior
                    interes_p=self.interes_periodo(self.saldo_inicial[n_ciclo],self.interes[n_ciclo])
                    
                    #Se aplica la logica necesaria para elegir una opcion u otra de calculo dependiendo del tipo de interes
                    if self.metodo[n_ciclo]=='cuota constante':
                        #Metodo Cuota Constante
                        anualidad=self.anualidad_constante(self.capital_prestado[n_ciclo],self.interes[n_ciclo],vencimiento)
                    

                    elif self.metodo[n_ciclo] =='principal constante':
                        #Metodo Principal Constante
                        anualidad=self.anualidad_principal_constante(a,interes_p)

                    else:
                        #Metodo bullet/ballon
                        vencimiento = ((fecha.year - self.fecha_actual.year) * 12 + (fecha.month - self.fecha_actual.month))
                        anualidad=self.anualidad_bullet(self.saldo_inicial[n_ciclo],self.interes[n_ciclo],year,vencimiento)

                    #Metodos de calculo base para la tabla de amortizacion
                    amortizacion_capital=self.amortizacion_capital(anualidad,interes_p)

                    capital_amortizado=self.capital_amortizado(amortizacion_capital,
                                                                            self.cap_amort_anterior)

                    pendiente=self.capital_pendiente(self.saldo_inicial[n_ciclo],amortizacion_capital) 
                 
                    #Igualamos el saldo final al saldo que quede pendiente en ese periodo una vez se ha restado el saldo amortizado
                    self.saldo_final=pendiente
                    
                    if pendiente<=0:
                        amortizacion_capital+=pendiente
                        capital_amortizado+=pendiente
                        pendiente=0
                        self.saldo_final=pendiente
              
                    saldo_promedio,medio_reprecio=self.saldo_capital_promedio(self.saldo_inicial[n_ciclo],self.fecha_constitucion,
                                                               fecha_cuota,self.saldo_final,estado_reprecio)
                  
                    #Ejecutamos las funciones de los calculos y sacamos por pantalla un
                    #mensaje u otro para comprobar el codigo
                    ajuste_neto=self.ajuste_neto_recursos(saldo_promedio,
                                                        tasa_transferencia_interna_base[n_ciclo])
                    
                    ingreso_real=self.ingreso_interes_real(saldo_promedio,
                                                            self.tasa_cliente[n_ciclo])
                    
                    # amortizado_periodo=self.capital_amortizado_periodo(self.saldo_final[n_ciclo],
                    #                                                     self.saldo_inicial[n_ciclo])
                    self.fecha_prox_rev[n_ciclo]=""
                    self.fecha_ult_reno[n_ciclo]=""
                    #Insertamos en el Dataframe los datos calculados en este periodo como una nueva fila
                    nueva_fila = {
                    "Pago de Cuota": fecha_cuota,
                    "Estado Reprecio":estado_reprecio,
                    "Ultimo Reprecio":self.fecha_ult_reno[n_ciclo],
                    "Proximo Reprecio":self.fecha_prox_rev[n_ciclo],
                    "Fecha vencimiento":self.fecha_vencimiento[n_ciclo],
                    "Tipo de acuerdo":tipo,
                    "Metodo de Amortizacion":self.metodo[n_ciclo],
                    "Tasa Interes":self.interes[n_ciclo],
                    "Interes": interes_p,
                    "Cuota": anualidad,
                    # "Amortizado_periodo":amortizado_periodo,
                    "Amortizacion en Periodo": amortizacion_capital,
                    "Capital Amortizado": capital_amortizado,
                    "Saldo Inicial": self.saldo_inicial[n_ciclo],
                    "Capital Promedio": saldo_promedio,
                    "Saldo Final": self.saldo_final,
                    "ajuste neto recurso": ajuste_neto,
                    "ingresos financieros": ingreso_real,
                    # "Frecuencia De Pago":self.frecuencia_pago[n_ciclo], 
                    # "Unidad Frecuencia De Pago":self.unidad_frec_pago[n_ciclo]
                    
                    }  
                elif tipo=="mixto":
                    fecha_cuota=datetime.date(año_actual,mes_actual,fecha_ultima_cuota.day)
                    estado_reprecio=self.estado_revision_mixto(fecha_cuota,n_ciclo)
                    if estado_reprecio=="X":
                        if self.estado_mixto==0:
                            # self.fecha_ult_reno[n_ciclo]=self.fecha_prox_rev[n_ciclo]
                            self.estado_mixto=1
                            
                        else:
                           
                            self.estado_mixto=0
                    if self.estado_mixto==1:
                        
                        if estado_reprecio=="X":
                            self.tasa_cliente[n_ciclo]=self.recalculo_tasa_cliente(self.tasa_cliente[n_ciclo],self.curva[n_ciclo],self.spread[n_ciclo],fecha_cuota,tipo)
                            tasa_transferencia_interna[n_ciclo]=self.recalculo_tasa_transferencia(tasa_transferencia_interna[n_ciclo],self.tasa_interes_deudor[n_ciclo],
                                                                                                    self.tasa_cliente[n_ciclo])
                                
                        fecha_cuota=fecha_cuota.strftime("%d-%m-%Y")
                        # co_restado=self.capital_prestado[n_ciclo]-self.cap_amort_anterior
                        interes_p=self.interes_periodo(self.saldo_inicial[n_ciclo],self.tasa_cliente[n_ciclo])
                        
                        #Se aplica la logica necesaria para elegir una opcion u otra de calculo dependiendo del tipo de interes
                        if self.metodo[n_ciclo]=='cuota constante':
                            #Metodo Cuota Constante
                            if estado_reprecio=="X" or year==1:
                            
                                anualidad=self.anualidad_constante(self.saldo_inicial[n_ciclo],self.tasa_cliente[n_ciclo],vencimiento)
                                

                        elif self.metodo[n_ciclo] =='principal constante':
                            #Metodo Principal Constante
                            anualidad=self.anualidad_principal_constante(a,interes_p)

                        else:
                            #Metodo bullet/ballon
                            vencimiento = ((fecha.year - self.fecha_actual.year) * 12 + (fecha.month - self.fecha_actual.month))
                            anualidad=self.anualidad_bullet(self.saldo_inicial[n_ciclo],self.tasa_cliente[n_ciclo],year,vencimiento)

                        #Metodos de calculo base para la tabla de amortizacion
                        amortizacion_capital=self.amortizacion_capital(anualidad,interes_p)

                        capital_amortizado=self.capital_amortizado(amortizacion_capital,
                                                                                self.cap_amort_anterior)

                        pendiente=self.capital_pendiente(self.saldo_inicial[n_ciclo],amortizacion_capital) 
                    
                        #Igualamos el saldo final al saldo que quede pendiente en ese periodo una vez se ha restado el saldo amortizado
                        self.saldo_final=pendiente
                        
                        if pendiente<=0:
                            amortizacion_capital+=pendiente
                            capital_amortizado+=pendiente
                            pendiente=0
                            self.saldo_final=pendiente
                
                        saldo_promedio,medio_reprecio=self.saldo_capital_promedio(self.saldo_inicial[n_ciclo],self.fecha_constitucion,
                                                                fecha_cuota,self.saldo_final,estado_reprecio)
                    
                        #Ejecutamos las funciones de los calculos y sacamos por pantalla un
                        #mensaje u otro para comprobar el codigo


                        ajuste_neto=self.ajuste_neto_recursos_reprecio(saldo_promedio,medio_reprecio,tasa_transferencia_interna_base[n_ciclo],
                                                            tasa_transferencia_interna[n_ciclo])
                        
                        ingreso_real=self.ingreso_interes_real_reprecio(saldo_promedio,medio_reprecio,
                                                                self.tasa_interes_deudor[n_ciclo])

                    else:
                        fecha_cuota=fecha_cuota.strftime("%d-%m-%Y")  
                        interes_p=self.interes_periodo(self.saldo_inicial[n_ciclo],self.interes[n_ciclo])
                        
                        #Se aplica la logica necesaria para elegir una opcion u otra de calculo dependiendo del tipo de interes
                        if self.metodo[n_ciclo]=='cuota constante':
                            #Metodo Cuota Constante
                            anualidad=self.anualidad_constante(self.capital_prestado[n_ciclo],self.interes[n_ciclo],vencimiento)
                        

                        elif self.metodo[n_ciclo] =='principal constante':
                            #Metodo Principal Constante
                            anualidad=self.anualidad_principal_constante(a,interes_p)

                        else:
                            #Metodo bullet/ballon
                            vencimiento = ((fecha.year - self.fecha_actual.year) * 12 + (fecha.month - self.fecha_actual.month))
                            anualidad=self.anualidad_bullet(self.saldo_inicial[n_ciclo],self.interes[n_ciclo],year,vencimiento)

                        #Metodos de calculo base para la tabla de amortizacion
                        amortizacion_capital=self.amortizacion_capital(anualidad,interes_p)

                        capital_amortizado=self.capital_amortizado(amortizacion_capital,
                                                                                self.cap_amort_anterior)

                        pendiente=self.capital_pendiente(self.saldo_inicial[n_ciclo],amortizacion_capital) 
                    
                        #Igualamos el saldo final al saldo que quede pendiente en ese periodo una vez se ha restado el saldo amortizado
                        self.saldo_final=pendiente
                        
                        if pendiente<=0:
                            amortizacion_capital+=pendiente
                            capital_amortizado+=pendiente
                            pendiente=0
                            self.saldo_final=pendiente
                
                        saldo_promedio,medio_reprecio=self.saldo_capital_promedio(self.saldo_inicial[n_ciclo],self.fecha_constitucion,
                                                                fecha_cuota,self.saldo_final,estado_reprecio="")
        
                        ajuste_neto=self.ajuste_neto_recursos(saldo_promedio,
                                                            tasa_transferencia_interna_base[n_ciclo])
                        
                        ingreso_real=self.ingreso_interes_real(saldo_promedio,
                                                                self.tasa_cliente[n_ciclo])
                        

                    nueva_fila = {
                    "Pago de Cuota": fecha_cuota,
                    "Estado Reprecio":estado_reprecio,
                    "Ultimo Reprecio":self.fecha_ult_reno[n_ciclo],
                    "Proximo Reprecio":self.fecha_prox_rev[n_ciclo],
                    "Fecha vencimiento":self.fecha_vencimiento[n_ciclo],
                    "Tipo de acuerdo":tipo,
                    "TT": tasa_transferencia_interna[n_ciclo],
                    "Metodo de Amortizacion":self.metodo[n_ciclo],
                    "Interes": interes_p,
                    "Cuota": anualidad,
                    # "Amortizado_periodo":amortizado_periodo,
                    "Amortizacion en Periodo": amortizacion_capital,
                    "Capital Amortizado": capital_amortizado,
                    "Saldo Inicial": self.saldo_inicial[n_ciclo],
                    "Capital Promedio": saldo_promedio,
                    "Capital Promedio*":medio_reprecio,
                    "Saldo Final": self.saldo_final,
                    "ajuste neto recurso": ajuste_neto,
                    "ingresos financieros": ingreso_real,
                    # "Frecuencia De Pago":self.frecuencia_pago[n_ciclo], 
                    # "Unidad Frecuencia De Pago":self.unidad_frec_pago[n_ciclo],
                    # "Reprecio":frecuencia_reprecio
                    } 
                       
                elif tipo=="variable":
                    fecha_cuota=datetime.date(año_actual,mes_actual,fecha_ultima_cuota.day)
                    estado_reprecio=self.estado_reprecio(lista_fecha_reprecio,fecha_cuota,frecuencia_reprecio,n_ciclo)
                    

                    if estado_reprecio=="X":
                        self.tasa_cliente[n_ciclo]=self.recalculo_tasa_cliente(self.tasa_cliente[n_ciclo],self.curva[n_ciclo],self.spread[n_ciclo],fecha_cuota,tipo)
                        tasa_transferencia_interna[n_ciclo]=self.recalculo_tasa_transferencia(tasa_transferencia_interna[n_ciclo],self.tasa_interes_deudor[n_ciclo],
                                                                                                  self.tasa_cliente[n_ciclo])
                            
                    fecha_cuota=fecha_cuota.strftime("%d-%m-%Y")
                    # co_restado=self.capital_prestado[n_ciclo]-self.cap_amort_anterior
                    interes_p=self.interes_periodo(self.saldo_inicial[n_ciclo],self.tasa_cliente[n_ciclo])
                    
                    #Se aplica la logica necesaria para elegir una opcion u otra de calculo dependiendo del tipo de interes
                    if self.metodo[n_ciclo]=='cuota constante':
                        #Metodo Cuota Constante
                        if year==1:
                           
                            anualidad=self.anualidad_constante(self.saldo_inicial[n_ciclo],self.tasa_cliente[n_ciclo],vencimiento)
                        else:
                            anualidad=self.anualidad_constante(self.saldo_inicial[n_ciclo],self.tasa_cliente[n_ciclo],((vencimiento-year)+1))                            

                    elif self.metodo[n_ciclo] =='principal constante':
                        #Metodo Principal Constante
                        anualidad=self.anualidad_principal_constante(a,interes_p)

                    else:
                        #Metodo bullet/ballon
                        vencimiento = ((fecha.year - self.fecha_actual.year) * 12 + (fecha.month - self.fecha_actual.month))
                        anualidad=self.anualidad_bullet(self.saldo_inicial[n_ciclo],self.tasa_cliente[n_ciclo],year,vencimiento)

                    #Metodos de calculo base para la tabla de amortizacion
                    amortizacion_capital=self.amortizacion_capital(anualidad,interes_p)

                    capital_amortizado=self.capital_amortizado(amortizacion_capital,
                                                                            self.cap_amort_anterior)

                    pendiente=self.capital_pendiente(self.saldo_inicial[n_ciclo],amortizacion_capital) 
                 
                    #Igualamos el saldo final al saldo que quede pendiente en ese periodo una vez se ha restado el saldo amortizado
                    self.saldo_final=pendiente
                    
                    if pendiente<=0:
                        amortizacion_capital+=pendiente
                        capital_amortizado+=pendiente
                        pendiente=0
                        self.saldo_final=pendiente
              
                    saldo_promedio,medio_reprecio=self.saldo_capital_promedio(self.saldo_inicial[n_ciclo],self.fecha_constitucion,
                                                               fecha_cuota,self.saldo_final,estado_reprecio)
                  
                    #Ejecutamos las funciones de los calculos y sacamos por pantalla un
                    #mensaje u otro para comprobar el codigo


                    ajuste_neto=self.ajuste_neto_recursos_reprecio(saldo_promedio,medio_reprecio,tasa_transferencia_interna_base[n_ciclo],
                                                        tasa_transferencia_interna[n_ciclo])
                    
                    ingreso_real=self.ingreso_interes_real_reprecio(saldo_promedio,medio_reprecio,
                                                            self.tasa_interes_deudor[n_ciclo])
                    
                    # amortizado_periodo=self.capital_amortizado_periodo(self.saldo_final[n_ciclo],
                    #                                                     self.saldo_inicial[n_ciclo])
                    #Realizamos un recalculo para la ultima cuota
                    #Insertamos en el Dataframe los datos calculados en este periodo como una nueva fila
                    nueva_fila = {
                    "Pago de Cuota": fecha_cuota,
                    "Estado Reprecio":estado_reprecio,
                    "Ultimo Reprecio":self.fecha_ult_reno[n_ciclo],
                    "Proximo Reprecio":self.fecha_prox_rev[n_ciclo],
                    "Fecha vencimiento":self.fecha_vencimiento[n_ciclo],
                    "Tipo de acuerdo":tipo,
                    "TT": tasa_transferencia_interna[n_ciclo],
                    "Metodo de Amortizacion":self.metodo[n_ciclo],
                    "Tasa Interes":self.tasa_cliente[n_ciclo],
                    "Interes": interes_p,
                    "Cuota": anualidad,
                    # "Amortizado_periodo":amortizado_periodo,
                    "Amortizacion en Periodo": amortizacion_capital,
                    "Capital Amortizado": capital_amortizado,
                    "Saldo Inicial": self.saldo_inicial[n_ciclo],
                    "Capital Promedio": saldo_promedio,
                    "Capital Promedio*":medio_reprecio,
                    "Saldo Final": self.saldo_final,
                    "ajuste neto recurso": ajuste_neto,
                    "ingresos financieros": ingreso_real,
                    # "Frecuencia De Pago":self.frecuencia_pago[n_ciclo], 
                    # "Unidad Frecuencia De Pago":self.unidad_frec_pago[n_ciclo],
                    "Reprecio":frecuencia_reprecio
                    }  
                    #esto sera para los tipos variables
                self.dataframe_salida = pd.concat([self.dataframe_salida, 
                                                   pd.DataFrame([nueva_fila])], ignore_index=True)
                
                self.saldo_inicial[n_ciclo]=self.saldo_final
                year+=1
                
                if proyecciones<=0 or pendiente==0:
                    bucle=False
          
            n_ciclo+=1
            self.fecha_reprecio_variable=0
        # Exportar el DataFrame a un archivo Excel
        self.dataframe_salida.to_excel("resultado_acuerdos.xlsx", index=False)
        os.system('cls')
        print("================================================\nData Frame Generado Correctamente\n================================================")
        return self.dataframe_salida