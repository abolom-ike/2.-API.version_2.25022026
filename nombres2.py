import random

def obtener_perfil_aleatorio(idGenero_vapi, conexion):
    try:
        with conexion.cursor() as cursor:
            # Obtener todos los perfiles activos del género
            cursor.execute("""
                SELECT idPerfil_vapi, nombre, apellido_paterno, apellido_materno, edad
                FROM BI_VAPI_PERFILES_USR
                WHERE activo = 1 AND idGenero_vapi = %s
            """, (idGenero_vapi,))
            
            perfiles = cursor.fetchall()
            
            if not perfiles:
                return None  # No hay perfiles activos para este género
            
            # --- Elegir nombre y obtener su id y edad ---
            perfil_nombre = random.choice(perfiles)
            idPerfil_vapi = perfil_nombre[0]
            nombre = perfil_nombre[1]
            edad = perfil_nombre[4]

            # --- Elegir apellido paterno aleatorio ---
            apellidos_p = [p[2] for p in perfiles]      # columna apellido_paterno
            apellido_paterno = random.choice(apellidos_p)

            # --- Elegir apellido materno aleatorio, distinto del paterno ---
            apellidos_m = [p[3] for p in perfiles if p[3] is not None]
            apellido_materno = random.choice([a for a in apellidos_m if a != apellido_paterno])
            
            # Construir nombre completo
            nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}"
            
            # Obtener género desde la tabla de géneros
            cursor.execute("SELECT genero FROM bi_vapi_genero WHERE idGenero_vapi = %s", (idGenero_vapi,))
            genero = cursor.fetchone()[0]
            
            return idPerfil_vapi, nombre_completo, edad, genero

    except Exception as e:
        print("Ocurrió un error al obtener_perfil_aleatorio():", e)
        return None
