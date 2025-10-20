import pyodbc
import json

#with open('C:\\Users\\alovalle\\Desktop\\Api_META\\config.json', 'r') as file: config = json.load(file)
# with open('S:\SSIS_MX\Agente VAPI\API\config.json', 'r') as file: config = json.load(file)
with open('S:\\SSIS_MX\\Agente VAPI\\API\\utils\\config.json', 'r') as file: config = json.load(file)



"""
direccion_servidor = config['BD_DEV']['DIRECCION_SERVER']
nombre_bd = config['BD_DEV']['NOMBRE_BASE']
nombre_usuario = config['BD_DEV']['USR']
password = config['BD_DEV']['PWD']
"""

"""
direccion_servidor = config['TEST']['DIRECCION_SERVER']
nombre_bd = config['TEST']['NOMBRE_BASE']
nombre_usuario = config['TEST']['USR']
password = config['TEST']['PWD']
"""


direccion_servidor = config['BD_PROD']['DIRECCION_SERVER']
nombre_bd = config['BD_PROD']['NOMBRE_BASE']
nombre_usuario = config['BD_PROD']['USR']
password = config['BD_PROD']['PWD']


try:
    #conexion = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER=' + direccion_servidor+';DATABASE='+nombre_bd+';UID='+nombre_usuario+';PWD=' + password)
    
    conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + direccion_servidor+';DATABASE='+nombre_bd+';UID='+nombre_usuario+';PWD=' + password)

    # OK! conexión exitosa
except Exception as e:
    # Atrapar error
    print("Ocurrió un error al conectar a SQL Server: ", e)