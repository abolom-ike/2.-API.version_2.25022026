import os

def generar_arbol_limitado(ruta_directorio, archivo_salida, max_nivel=3):
    def recorrer_directorio(ruta, prefijo="", nivel=1):
        if nivel > max_nivel:
            return ""
        elementos = sorted(os.listdir(ruta))
        contenido = ""
        for i, nombre in enumerate(elementos):
            ruta_completa = os.path.join(ruta, nombre)
            es_ultimo = (i == len(elementos) - 1)
            conector = "└── " if es_ultimo else "├── "
            contenido += prefijo + conector + nombre + "\n"
            if os.path.isdir(ruta_completa):
                nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
                contenido += recorrer_directorio(ruta_completa, nuevo_prefijo, nivel + 1)
        return contenido

    nombre_raiz = os.path.basename(os.path.abspath(ruta_directorio))
    estructura = nombre_raiz + "\n"
    estructura += recorrer_directorio(ruta_directorio)

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(estructura)

    print(f"Estructura (hasta {max_nivel} niveles) guardada en: {archivo_salida}")


# ======= USO =======
ruta_proyecto = "./"  # Carpeta actual
archivo_salida = "estructura_3_niveles.txt"

# Puedes cambiar max_nivel si quieres más o menos profundidad
generar_arbol_limitado(ruta_proyecto, archivo_salida, max_nivel=3)
