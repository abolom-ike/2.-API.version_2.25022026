import random
import pandas as pd
from utils.conexionDB import conexion
import warnings

warnings.filterwarnings("ignore")


def truncate_stage():
    try:
        with conexion.cursor() as cursor:
            consultaphoneNumbers = "truncate table bi_vapi_sta_carga"
            cursor.execute(consultaphoneNumbers)       
    except Exception as e:
        print("Ocurrio un error al truncar las tablas : " , e)


def obtener_configuracion():
    try:
        with conexion.cursor() as cursor:
            ejecutarTabla = """select  
                            t1.clServicio, t1.Servicio, t1.clSubServicio, t1.SubServicio, t1.NombreCuenta, t2.idPromptVapi, t2.prompt
                        from bi_vapi_llamada_agente_config t1 
                            inner join bi_vapi_prompt t2 on t1.idPromptVapi = t2.idPromptVapi and t1.clServicio = t2.clServicio and t1.clSubServicio = t2.clSubServicio and t1.clcuenta = t2.clcuenta
                            where t1.activo = 1"""
            DataFBU = pd.read_sql(ejecutarTabla, conexion)
    except Exception as e:
        print("Ocurrio un error al obtener la tabla : " , e)
    return DataFBU

def obtener_config_api_agente(idAgenteVapi):
    try:
        with conexion.cursor() as cursor:
            # ejecutarTabla = "select * from BI_SFTP where IdSFTP = 3"
            ejecutarTabla = "select * from bi_vapi_config_api where idAgenteVapi = %d" % (idAgenteVapi)
            DataFBU = pd.read_sql(ejecutarTabla, conexion)
    except Exception as e:
        print("Ocurrio un error al obtener la tabla : " , e)
    return DataFBU

def obtener_llamadas_a_procesar(agente):
    try:
        with conexion.cursor() as cursor:
            ejecutarTabla = """select * from bi_vapi_sta_carga where procesada = 0 and idAgenteVapi = %d""" % (agente)
            DataFBU = pd.read_sql(ejecutarTabla, conexion)
    except Exception as e:
        print("Ocurrio un error al obtener la tabla : " , e)
    return DataFBU

def actualizar_procesada(id_llamada):
    try:
        with conexion.cursor() as cursor:
            cursor.execute("update bi_vapi_sta_carga set procesada = 1 where id_llamada = ?", (id_llamada,))
    except Exception as e:
        print("Ocurrio un error al actualizar la tabla : " , e)

def obtener_voz_perfil():
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT idVoz_vapi,Provider, VoiceId, idGenero_vapi FROM bi_vapi_voz_perfil WHERE activo = 1")
            voices = cursor.fetchall()
            idVoz_vapi, provider, voice_id, idGenero_vapi = random.choice(voices)
            return idVoz_vapi, provider, voice_id, idGenero_vapi
    except Exception as e:
        print("Ocurrio un error al def obtener_voz_perfil() : " , e)

def obtener_perfil(idGenero_vapi):
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                 select per.idPerfil_vapi,per.nombre, per.apellido_paterno, per.Apellido_materno, per.edad, gen.genero, per.clave from BI_VAPI_PERFILES_USR per
	            inner join bi_vapi_genero gen on per.idGenero_vapi = gen.idGenero_vapi where per.activo = 1 and per.idGenero_vapi = %d""" % (idGenero_vapi))
            names = cursor.fetchall()
            idPerfil_vapi,selected_name, apellido_paterno, apellido_materno, edad, gender, clave = random.choice(names)
            return idPerfil_vapi,selected_name, apellido_paterno, apellido_materno, edad, gender, clave
    except Exception as e:
        print("Ocurrio un error al obtener_perfil() : " , e)


def insertar_histo(df):
    try:
        with conexion.cursor() as cursor:
            for index, row in df.iterrows():
                cursor.execute("INSERT INTO bi_vapi_llamada_historico([idAgenteVapi],[phone_number],[idPromptVapi],[numero],[nombre],[clServicio],[clSubServicio],[id_llamada],[phoneNumberId],[type],[createdAt],[orgId],[status],[phoneCallProvider],[phoneCallProviderId],[customer_number],[procesada],[transcripcion],[recordingUrl],[uuid_solicitud_llamada],[NombreArhivoExcel],[idVoz_vapi],[idPerfil_vapi],[ext]) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                               row.idAgenteVapi, row.phone_number, row.idPromptVapi, row.numero, row.nombre, row.clServicio, row.clSubServicio, row.id_llamada, row.phoneNumberId, row.type, row.createdAt, row.orgId, row.status, row.phoneCallProvider, row.phoneCallProviderId, row.customer_number, row.procesada, row.transcripcion, row.recordingUrl,row.uuid_solicitud_llamada,row.NombreArhivoExcel,row.idVoz_vapi,row.idPerfil_vapi,row.ext)
    except Exception as e:
        print("Ocurrio un error al insertar en la tabla de insertar_histo : ", e)

def insertar_detalle_llamada(lista):
    try:
        #print(len(lista))
        with conexion.cursor() as cursor:
            for index, row in lista.iterrows():
                cursor.execute("INSERT INTO bi_vapi_sta_carga([idAgenteVapi],[phone_number],[idPromptVapi],[numero],[nombre],[clServicio],[clSubServicio],[id_llamada],[phoneNumberId],[type],[createdAt],[orgId],[status],[phoneCallProvider],[phoneCallProviderId],[customer_number],[procesada],[uuid_solicitud_llamada],[NombreArhivoExcel],[idVoz_vapi],[idPerfil_vapi],[ext]) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row.idAgenteVapi, row.phone_number, row.idPromptVapi , row.numero, row.nombre, row.clServicio, row.clSubServicio, row.id_llamada, row.phoneNumberId, row.type,row.createdAt,row.orgId,row.status,row.phoneCallProvider,row.phoneCallProviderId,row.customer_number,row.procesada,row.uuid_file,row.NombreArhivoExcel,row.idVoz_vapi,row.idPerfil_vapi,row.extension)

    except Exception as e:
        print("Ocurrio un error al insertar en la tabla de insertar_detalle_llamada : " , e)

def cerrarConexion():
    conexion.close()
