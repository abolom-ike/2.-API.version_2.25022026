# from coreApi import genera_llamadas
# from coreApi import procesa_llamadas
from scripts.CX.manageAgenteCX import manageAgenteCX
from coreApi import genera_llamada, getLlamada#, genera_llamada_con_extension
from scripts.funciones.funcionesDB import obtener_llamadas_a_procesar
import time
import pandas as pd


def agente_cx(agente,operacion, URL, phoneNumberId, API_KEY, AGENT_ID, rutaArchivoProcesar, rutaArchivoProcesado,tieneRedireccionamiento):
    # aquí va el menú
    if operacion == "1":
        # call_agent_outbound(URL,phoneNumberId, API_KEY)
        manageAgenteCX()
        # genera_llamadas(URL, phoneNumberId, API_KEY, AGENT_ID, rutaArchivoProcesar, rutaArchivoProcesado)
        print("operación 1 en proceso")
    if operacion == "2":
        print("operación 2 en proceso")
        procesa_llamadas(URL,API_KEY,agente)


def procesa_llamadas(URL, API_KEY,agente):
    headers_llamada = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    df_llamadas_a_procesar = obtener_llamadas_a_procesar(agente)
    print(df_llamadas_a_procesar)
    if len(df_llamadas_a_procesar) >= 1:
        print("Llamadas a procesar: ", len(df_llamadas_a_procesar))
        for idx, fila in df_llamadas_a_procesar.iterrows():
            df2 = fila.to_frame().T.reset_index(drop=True)
            # print(df2)
            getLlamada(df2, URL, headers_llamada)
            time.sleep(5)
    else:
        print("No hay llamadas a procesar")