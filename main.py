import sys
import pandas as pd
from scripts.funciones.funcionesDB import cerrarConexion
from scripts.funciones.funcionesDB import obtener_config_api_agente
from scripts.Capacitacion.agenteCapacitacion import agente_capacitacion
from scripts.CX.agenteCx import agente_cx

if __name__ == "__main__":
    print("inicio 02-07-2025")
    if len(sys.argv) < 3:
        print("Uso: python main.py idAgente operacion(1 Genera Llamada o 2 Procesa Llamada)")
        sys.exit(1)  # salir con error
    
    agente = sys.argv[1]#id agente
    operacion = sys.argv[2] #operacion
    

    agente = int(agente)
    df_config = obtener_config_api_agente(agente)

    URL = df_config["url_call"][0]
    API_KEY = df_config["api_key"][0]
    AGENT_ID = df_config["agent_id"][0]
    phoneNumberId = df_config["phone_number_id"][0]
    rutaArchivoProcesar = df_config["rutaArchivoProcesar"][0]
    rutaArchivoProcesado = df_config["rutaArchivoProcesado"][0]
    tieneRedireccionamiento = df_config["tieneRedireccionamiento"][0]
    # tieneRedireccionamiento = 0

    if agente == 1:
        agente_capacitacion(agente,operacion,URL, phoneNumberId, API_KEY, AGENT_ID, rutaArchivoProcesar, rutaArchivoProcesado,tieneRedireccionamiento)
    if agente == 2:
        agente_cx(agente,operacion,URL, phoneNumberId, API_KEY, AGENT_ID, rutaArchivoProcesar, rutaArchivoProcesado,tieneRedireccionamiento)

    cerrarConexion()

    




