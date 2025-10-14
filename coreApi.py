import requests
import time
import json
from scripts.funciones.funcionesDB import insertar_detalle_llamada
from scripts.funciones.funcionesDB import actualizar_procesada
from scripts.funciones.funcionesDB import insertar_histo
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial, Pause

TRIGGERS = [
    "me quiero quejar",
    "quiero poner una queja",
    "tengo una queja",
    "quiero hablar con un supervisor",
    "quiero levantar una queja",
    "quiero generar una queja"
]


def genera_llamada(URL,headers,json,df_llamadas_sta):
    response = requests.post(URL, headers=headers, json=json)
    print(response.status_code)
    print(response.text)
    if response.status_code == 201:
        print("Llamada generada correctamente")
        json_res = response.json()
        print(json_res)
        df_llamadas_sta['id_llamada'] = [json_res['results'][0]['id']]
        df_llamadas_sta['phoneNumberId'] = [json_res['results'][0]['phoneNumberId']]
        df_llamadas_sta['type'] = [json_res['results'][0]['type']]
        df_llamadas_sta['createdAt'] = [json_res['results'][0]['createdAt']]
        df_llamadas_sta['orgId'] = [json_res['results'][0]['orgId']]
        df_llamadas_sta['status'] = [json_res['results'][0]['status']]
        df_llamadas_sta['phoneCallProvider'] = [json_res['results'][0]['phoneCallProvider']]
        df_llamadas_sta['phoneCallProviderId'] = [json_res['results'][0]['phoneCallProviderId']]
        df_llamadas_sta['customer_number'] = [json_res['results'][0]['customer']['number']]

        print(df_llamadas_sta)
        insertar_detalle_llamada(df_llamadas_sta)

def getLlamada(df_llamadas_a_procesar, URL, headers_llamada):
        print("entro a getLlamada")
        id_llamada = df_llamadas_a_procesar['id_llamada'][0]
        URL = URL + "/" + id_llamada
        response_a_procesar = requests.get(URL, headers=headers_llamada)
        if response_a_procesar.status_code == 200:
            print("Llamada procesada correctamente")
            transcripcion = response_a_procesar.json().get("transcript", "")
            # print(transcripcion)
            recordingUrl = response_a_procesar.json().get("recordingUrl", "")
            status = response_a_procesar.json().get("status", "")
            # print(recordingUrl)
            df_llamadas_a_procesar["transcripcion"] = transcripcion
            df_llamadas_a_procesar["recordingUrl"] = recordingUrl
            df_llamadas_a_procesar["status"] = status
            insertar_histo(df_llamadas_a_procesar)
            actualizar_procesada(id_llamada)
            return
        else:
            print("Error al procesar la llamada")
            return
        
