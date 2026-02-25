# crear método para mover archivo a procesados
import os
import shutil

def mover_archivo_a_procesados(ruta_archivo,ruta_procesados):
     #mover archivo a procesados
    print("mover a procesados")
    procesar = ruta_archivo
    procesados = ruta_procesados
    procesar_contents = os.listdir(procesar)
    for i in range(len(procesar_contents)):
        # print(procesar_contents[i])
        ArchivoAMover = procesar + procesar_contents[i]
        RutaAMover = procesados + procesar_contents[i]
        # print(RutaAMover)
        cadena_es = '.snapshot'
        indice = RutaAMover.find(cadena_es)
        # print(indice)
        if indice == -1:
            shutil.move(ArchivoAMover ,RutaAMover )