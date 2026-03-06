#from coreApi import genera_llamadas
#from coreApi import procesa_llamadas
# import requests
import uuid
import os
import pandas as pd
import time
from scripts.funciones.funcionesDB import obtener_perfil, obtener_voz_perfil, obtener_configuracion
from scripts.funciones.funcionesDB import truncate_stage
from scripts.funciones.funcionesDB import insertar_detalle_llamada
from scripts.funciones.funcionesDB import cerrarConexion
from scripts.funciones.funcionesDB import obtener_llamadas_a_procesar
from scripts.funciones.funcionesDB import datos_prompt

#from scripts.funciones.funcionesDB import mover_archivo_a_procesados
from coreApi import genera_llamada, getLlamada##, genera_llamada_con_extension,genera_llamada_con_extension_prueba1

# método principal del agente de capacitación(selección de operación)
def agente_capacitacion(agente,operacion, URL, phoneNumberId, API_KEY, AGENT_ID, rutaArchivoProcesar, rutaArchivoProcesado,tieneRedireccionamiento):
    if operacion == "1":
        # call_agent_outbound(URL,phoneNumberId, API_KEY)
        if tieneRedireccionamiento != 1:
            genera_llamadas(URL, phoneNumberId, API_KEY, AGENT_ID,rutaArchivoProcesar, rutaArchivoProcesado)
            # genera_llamadas_extension(URL, phoneNumberId, API_KEY, AGENT_ID,rutaArchivoProcesar, rutaArchivoProcesado)
        else:
            genera_llamadas_con_redireccionamiento(URL, phoneNumberId, API_KEY, AGENT_ID,rutaArchivoProcesar, rutaArchivoProcesado)

    if operacion == "2":
        print("operación 2 en proceso")
        procesa_llamadas(URL,API_KEY,agente)


def genera_llamadas(URL, phoneNumberId, API_KEY, AGENT_ID, rutaArchivoProcesar, rutaArchivoProcesado):
    
    # headers petición a la API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    uuid_file = uuid.uuid1()
    archivos = os.listdir(rutaArchivoProcesar) 

    if len(archivos) >= 1:
        archivo = archivos[0]
        archivoExcel = rutaArchivoProcesar +  archivo
        df = pd.read_excel(archivoExcel)  
        df = df.fillna(' ') 

        df_config = obtener_configuracion()
        df_llamadas = df.merge(df_config, left_on=["clservicio", "clsubservicio"], right_on=["clServicio", "clSubServicio"], how="inner")

   
        for index, row in df_llamadas.iterrows():

            id_prompt                = row["idPromptVapi"]
            id_voz,edad_min,edad_max = datos_prompt(id_prompt)
            #id_buscado = 40
            idVoz_vapi,provider,voice_id, idGenero_vapi = obtener_voz_perfil(id_voz)
            print("idGenero_vapi:", idGenero_vapi)
            
            perfil = obtener_perfil(idGenero_vapi,edad_min,edad_max)
            print("perfil:", perfil)
            idPerfil_vapi,selected_name, apellido_paterno, apellido_materno, edad, gender, clave, domicilio = obtener_perfil(idGenero_vapi,edad_min,edad_max)
            print(df_llamadas)
            idAgenteVapi = row["idAgenteVapi"]
            phone_number = row["numero"]
            prompt =       row["prompt"]
            prompt =  prompt.format (
                gender           = gender,
                selected_name    = selected_name, 
                apellido_paterno = apellido_paterno, 
                apellido_materno = apellido_materno, 
                edad             = edad, 
                clave            = clave,
                domicilio        = domicilio
            )
            
            idPromptVapi     = row["idPromptVapi"]
            numero           = row["numero"]
            clServicio       = row["clservicio"]
            clSubServicio    = row["clsubservicio"]
            nombre           = row["nombre"]
            extension        = row["extension"]
            phone_number     = "+" + str(phone_number)
        # extension= "600543#"
            menu_digit       = "1" #"7"
            sub_menu_digit   = ""#"1"

        # provider = '11labs'
        # voice_id = '6HCwgZXWcrhF6ZoTZJkf'

        # # json para la petición con dinamismo de voz y perfil 
            json={
                "assistantId":   AGENT_ID,
                "phoneNumberId": phoneNumberId,
                "customers": [
                {
                    "number": phone_number
                }
                ],
                "assistantOverrides": {
                "variableValues": {
                    "prompt": prompt,
                    "extension": extension,   # extensión
                    "menu_digit": menu_digit,       # menú principal
                    "sub_menu_digit": sub_menu_digit    # submenú
                },
                "voice": {
                    "provider": provider,
                    "voiceId": voice_id
                    }
                }
            }

            df_llamadas_sta = pd.DataFrame()
            df_llamadas_sta['idAgenteVapi'] = [idAgenteVapi]
            df_llamadas_sta['idPromptVapi'] = [idPromptVapi]
            df_llamadas_sta['phone_number'] = [phone_number]
            df_llamadas_sta['numero'] = [numero]
            df_llamadas_sta['nombre'] = [nombre]
            df_llamadas_sta['clServicio'] = [clServicio]
            df_llamadas_sta['clSubServicio'] = [clSubServicio]
            df_llamadas_sta['procesada'] = 0
            df_llamadas_sta['uuid_file'] = [uuid_file]
            df_llamadas_sta['NombreArhivoExcel'] = [archivo]
            df_llamadas_sta['idVoz_vapi'] = [idVoz_vapi]
            df_llamadas_sta['idPerfil_vapi'] = [idPerfil_vapi]
            df_llamadas_sta['extension'] = [extension]
            genera_llamada(URL,headers,json,df_llamadas_sta)
            time.sleep(20)
        
    # mover_archivo_a_procesados(rutaArchivoProcesar,rutaArchivoProcesado)

    else:
        print("No hay archivo a procesar")


#método para procesar llamadas - una o muchas
def procesa_llamadas(URL, API_KEY,agente):
    headers_llamada = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    df_llamadas_a_procesar = obtener_llamadas_a_procesar(agente)
    df_llamadas_a_procesar = df_llamadas_a_procesar.fillna(' ')
    print(df_llamadas_a_procesar)
    if len(df_llamadas_a_procesar) >= 1:
        print("Llamadas a procesar: ", len(df_llamadas_a_procesar))
        for idx, fila in df_llamadas_a_procesar.iterrows():
            df2 = fila.to_frame().T.reset_index(drop=True)
            getLlamada(df2, URL, headers_llamada)
            time.sleep(5)
    else:
        print("No hay llamadas a procesar")


def genera_llamadas_con_redireccionamiento(URL, phoneNumberId, API_KEY, AGENT_ID, rutaArchivoProcesar, rutaArchivoProcesado):
    # headers petición a la API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    uuid_file = uuid.uuid1()

    archivos = os.listdir(rutaArchivoProcesar) 
    # print(archivos)
    
    # leer arcchivos de la ruta y tomar archivo -- validar que hay archivo a procesar sino mandar mensaje
    if len(archivos) >= 1:
        archivo = archivos[0]

        archivoExcel = rutaArchivoProcesar +  archivo

        df = pd.read_excel(archivoExcel)

        # print(df)    
        df_config = obtener_configuracion()

        df_llamadas = df.merge(df_config,
                               left_on =["clservicio", "clsubservicio"], 
                               right_on=["clServicio", "clSubServicio"], 
                               how="inner")

        for index, row in df_llamadas.iterrows():
            # print(df_llamadas)
            idAgenteVapi    = row["idAgenteVapi"]
            phone_number    = row["numero"]
            prompt          = row["prompt"]
            idPromptVapi    = row["idPromptVapi"]
            numero          = row["numero"]
            clServicio      = row["clservicio"]
            clSubServicio   = row["clsubservicio"]
            nombre          = row["nombre"]
            phone_number = "+" + str(phone_number)

            # # json para la petición
            json={
                "assistantId": AGENT_ID,
                "phoneNumberId": phoneNumberId,
                "customers": [
                {
                    "number": phone_number
                }
                ],
                "assistantOverrides": {
                "variableValues": {
                    "prompt": prompt
                }
                }
            }
            df_llamadas_sta = pd.DataFrame()

            df_llamadas_sta['idAgenteVapi']      = [idAgenteVapi]
            df_llamadas_sta['idPromptVapi']      = [idPromptVapi]
            df_llamadas_sta['phone_number']      = [phone_number]
            df_llamadas_sta['numero']            = [numero]
            df_llamadas_sta['nombre']            = [nombre]
            df_llamadas_sta['clServicio']        = [clServicio]
            df_llamadas_sta['clSubServicio']     = [clSubServicio]
            df_llamadas_sta['procesada']         = 0
            df_llamadas_sta['uuid_file']         = [uuid_file]
            df_llamadas_sta['NombreArhivoExcel'] = [archivo]
            # genera_llamada_con_redireccionamiento(URL,headers,json,df_llamadas_sta)
            ## hacer prueba con varios números 
            time.sleep(30)
            
        # mover_archivo_a_procesados(rutaArchivoProcesar,rutaArchivoProcesado)

    else:
        print("No hay archivo a procesar")


# def genera_llamadas_extension(URL, phoneNumberId, API_KEY, AGENT_ID, rutaArchivoProcesar, rutaArchivoProcesado):
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }   
#     json = {
#         "assistantId": AGENT_ID,
#         "phoneNumberId": phoneNumberId,
#         "customers": [
#         {
#             # "number": "+525619915654" 
#             "number": "+525554800970" 
#         }   
#         ],
#         "assistantOverrides": {
#             "variableValues": {
#                 "prompt": "prueba con extensión",
#                 "extension": "600543#"   # <-- Aquí defines la extensión
#             }
#         }
#     }
#     df_llamadas_sta = pd.DataFrame()
#     genera_llamada_con_extension_prueba1(URL,headers,json,df_llamadas_sta)

# def genera_llamada_con_extension_prueba1(URL,headers,json,df_llamadas_sta):
#     response = requests.post(URL, headers=headers, json=json)
#     print(f"Response: {response.status_code}")
#     print(f"Body: {response.json()}")
    
#     if response.status_code == 201:
#         print("Llamada generada correctamente")
#         json_res = response.json()
#         print(json_res)
#         call_id = json_res['results'][0]['id']
#         print(f"Call ID: {call_id}")
#         print(f"Llamada creada. Call ID: {call_id}")
    


