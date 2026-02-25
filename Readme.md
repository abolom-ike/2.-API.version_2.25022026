Cambios:
1) archivo main.py 

original: 
rutaArchivoProcesar = df_config["rutaArchivoProcesar"][0]
#rutaArchivoProcesado = df_config["rutaArchivoProcesado"][0]

Cambio a ruta relativa:
rutaArchivoProcesar = "data/Capacitacion/procesar/"
rutaArchivoProcesado = "data/Capacitacion/procesado/"

2) Archivo funciones DB.py

  función: obtener_voz_perfil

  original: def obtener_voz_perfil()
  cambio  : def obtener_voz_perfil(id_buscado)

  original: cursor.execute("SELECT idVoz_vapi,Provider, VoiceId, idGenero_vapi FROM bi_vapi_voz_perfil WHERE activo = 1")
  cambio:   cursor.execute("SELECT idVoz_vapi,Provider, VoiceId, idGenero_vapi FROM bi_vapi_voz_perfil WHERE idVoz_vapi = ?, (id_buscado,))
 
  original: voices = cursor.fetchall()
  cambio  : voices = cursor.fetchone()

  original:   idVoz_vapi, provider, voice_id, idGenero_vapi = random.choice(voices)
              return idVoz_vapi, provider, voice_id, idGenero_vapi

  cambio: if voices:
                idVoz_vapi, provider, voice_id, idGenero_vapi = voices
                return idVoz_vapi, provider, voice_id, idGenero_vapi
          else:
                return none

3) archivo agenteCapacitacion.py

se agregó la linea id_buscado = 37 en la función genera_llamadas para colocar el id de la voz que se requiera 