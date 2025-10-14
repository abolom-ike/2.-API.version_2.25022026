# config.py
import os
from dotenv import load_dotenv


# Obtener la ruta del directorio donde se encuentra este archivo (config.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carga las variables del archivo .env al entorno
# En config.py
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)

"""
Archivo de configuración centralizado para el Sistema de Encuestas Telefónicas.
Contiene todas las configuraciones necesarias para la integración con APIs.
"""
CONFIG = {
    "vapi": {
        'api_key': os.getenv('VAPI_API_KEY'),
        'assistant_id': os.getenv('VAPI_ASSISTANT_ID'),
        'phone_id': os.getenv('VAPI_PHONE_ID')
    },
    "twilio": {
        'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
        'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
        'phone_number': os.getenv('TWILIO_PHONE_NUMBER')
    },
    "files": {
        # 'excel_path': 'Base usuarios.xlsx', # Ruta a tu archivo de datos del cliente
        'excel_path': 'Base usuarios interna IKE.xlsx', # Ruta a tu archivo de datos del cliente
        
        #'excel_path': 'Base usuarios remarcado.xlsx',
        'backup_folder': r'C:\Users\jayala\OneDrive - ikeasistencia.com\Documentos\J_Proyects\Agente_encuestas_AI\Backups',
        # 'prompt_path': os.path.join(BASE_DIR, 'Prompt.txt') # Ruta a tu archivo de prompt
        'prompt_path': os.path.join(BASE_DIR, 'Prompt proveedor.txt') # Ruta a tu archivo de prompt
        
                         #r'C:\Users\jayala\OneDrive - ikeasistencia.com\Documentos\J_Proyects\Agente_encuestas_AI\Prompt.txt'  
    },                 
    "call_settings": {
        'delay_between_calls': 30,
        'max_retries': 3
    },
    "logging": {
        'level': 'INFO',
        'file_path': 'sistema_de_logs.log'
    },
    #Se definen aquí los nombres de las columnas para evitar.
        "excel_columns": {
        "required": [
            'Expediente', 'Fecha_Expediente', 'Hora_Expediente', 'Cuenta',
            'Servicio', 'Subservicio', 'Nombre_Usuario', 'Telefono'  
        ],
        "tracking": [
            'call_id', 'call_status', 'call_timestamp', 'call_success',
            'call_duration', 'call_transcript'
        ],
        #Se mapean los nombres clave para usarlos en el código de forma segura.
        "mapping": {
            "name": "Nombre_Usuario",  
            "phone": "Telefono"    
        }
    }
}