# sistema_de_encuestas.py
import os
import shutil
import time
import logging
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, List, Optional
from twilio.rest import Client

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

class SurveyCallSystem:
    """
    Clase principal que maneja toda la lógica para el sistema de encuestas telefónicas.
    """

    def __init__(self, config: Dict):
        """
        Inicializa el sistema con la configuración centralizada.
        """
        self.config = config
        self.vapi_config = config['vapi']
        self.twilio_config = config['twilio']
        self.files_config = config['files']
        
        #Mapeo de columnas.
        self.col_map = config['excel_columns']['mapping']
        self.col_name = self.col_map['name']
        self.col_phone = self.col_map['phone']
        
        self.vapi_headers = {
            'Authorization': f'Bearer {self.vapi_config["api_key"]}',
            'Content-Type': 'application/json'
        }
        self.vapi_base_url = 'https://api.vapi.ai'
        self.twilio_client = Client(
            self.twilio_config['account_sid'],
            self.twilio_config['auth_token']
        )

    def backup_excel_file(self):
        """
        Crea una copia de seguridad del archivo Excel antes de guardarlo.
        """
        source_path = self.files_config['excel_path']
        backup_folder = self.files_config['backup_folder']
        
        if not os.path.exists(source_path):
            logger.warning("No se encontró el archivo Excel para respaldar.")
            return

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
            logger.info(f"Carpeta de respaldo creada en: {backup_folder}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}_{os.path.basename(source_path)}"
        backup_path = os.path.join(backup_folder, backup_filename)
        
        try:
            shutil.copy2(source_path, backup_path)
            logger.info(f"Respaldo creado exitosamente en: {backup_path}")
        except Exception as e:
            logger.error(f"No se pudo crear el respaldo del archivo Excel: {e}")

    def normalize_phone_number(self, phone) -> str:
        """
        Asegura que el número de teléfono esté en formato E.164 (+52XXXXXXXXXX).
        También maneja números leídos como notación científica desde Excel.
        """
        phone_str = str(phone).strip()
        
        if 'e' in phone_str.lower():
            try:
                phone_str = f"{int(float(phone_str))}"
            except (ValueError, TypeError):
                return ""

        digits = ''.join(filter(str.isdigit, phone_str))

        if not digits:
            return ""

        if len(digits) == 10:
            return f"+52{digits}"
        
        if len(digits) == 12 and digits.startswith('52'):
             return f"+{digits}"

        if phone_str.startswith('+'):
            return phone_str
        
        logger.warning(f"Número de teléfono con formato no estándar: {phone}. Se intentará usar tal cual.")
        return phone_str

    def load_contacts_from_excel(self) -> pd.DataFrame:
        """
        Carga los contactos desde el archivo Excel.
        """
        try:
            df = pd.read_excel(self.files_config['excel_path'], dtype=str)
            df = df.fillna('')
            logger.info(f"Cargados {len(df)} contactos desde {self.files_config['excel_path']}")
            return df
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {self.files_config['excel_path']}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error al cargar contactos: {e}")
            return pd.DataFrame()

    def save_contacts_to_excel(self, df: pd.DataFrame):
        """
        Guarda los contactos actualizados en el archivo Excel, creando un respaldo primero.
        """
        self.backup_excel_file()
        try:
            df.to_excel(self.files_config['excel_path'], index=False)
            logger.info(f"Contactos guardados en {self.files_config['excel_path']}")
        except Exception as e:
            logger.error(f"Error al guardar contactos: {e}")


    def create_vapi_call(self, contact_row: pd.Series) -> Optional[Dict]:
        """
        Crea una llamada usando VAPI, definiendo el asistente directamente en la llamada.
        """
        # Obtener y normalizar datos del contacto 
        phone_raw = contact_row.get(self.col_phone)
        phone_number = self.normalize_phone_number(phone_raw)
        customer_name = contact_row.get(self.col_name)

        if not phone_number:
            logger.error(f"Número de teléfono inválido para {customer_name} después de normalizar.")
            return None

        try:
            #  Personalizar el prompt principal (el guion del Agente IA) 
            with open(self.files_config['prompt_path'], 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            personalized_prompt = prompt_template.replace('{{Nombre_Usuario}}', str(contact_row.get('Nombre_Usuario', '')))
            personalized_prompt = personalized_prompt.replace('{{Telefono}}', str(contact_row.get('Telefono', '')))
            personalized_prompt = personalized_prompt.replace('{{Subservicio}}', str(contact_row.get('Subservicio', '')))
            personalized_prompt = personalized_prompt.replace('{{cuenta}}', str(contact_row.get('Cuenta', '')))
            personalized_prompt = personalized_prompt.replace('{{expediente}}', str(contact_row.get('Expediente', '')))
            personalized_prompt = personalized_prompt.replace('{{fecha_servicio}}', str(contact_row.get('Fecha_Expediente', '')))
            personalized_prompt = personalized_prompt.replace('{{hora_servicio}}', str(contact_row.get('Hora_Expediente', '')))

            # Mensaje inicial
            first_message_template = "Hola, buen día le llamo de {{cuenta}}. ¿Me comunico con {{Nombre_Usuario}}?"
            personalized_first_message = first_message_template.replace('{{cuenta}}', str(contact_row.get('Cuenta', '')))
            personalized_first_message = personalized_first_message.replace('{{Nombre_Usuario}}', str(contact_row.get('Nombre_Usuario', '')))
            
             # mensaje para el buzón de voz 
            #voicemail_template = "Hola {{Nombre_Usuario}}, mi nombre es Carmen, su asistente virtual de {{cuenta}}. Le llamo para hacerle una breve encuesta de satisfacción del servicio {{Subservicio}} que recibió el día {{fecha_servicio}}. Me pondré en contacto con usted más tarde. ¡Que tenga un excelente día!"
            #personalized_voicemail = voicemail_template.replace('{{Nombre_Usuario}}', str(contact_row.get('Nombre_Usuario', '')))
            #personalized_voicemail = personalized_voicemail.replace('{{cuenta}}', str(contact_row.get('Cuenta', '')))
            #personalized_voicemail = personalized_voicemail.replace('{{Subservicio}}', str(contact_row.get('Subservicio', '')))
            #personalized_voicemail = personalized_voicemail.replace('{{fecha_servicio}}', str(contact_row.get('Fecha_Expediente', '')))


        except Exception as e:
            logger.error(f"Error al leer o procesar el archivo de prompt: {e}")
            return None

        url = f"{self.vapi_base_url}/call"
        
        # Construir el cuerpo de la llamada a la API 
        call_data = {
            "phoneNumberId": self.vapi_config['phone_id'],
            "customer": {
                "number": phone_number,
                "name": customer_name
            },
            "assistant": {
                "name": "Carmen", #Encuesta de Calidad post-servicio
                "language": "es-419", # Define el idioma para toda la conversación 
                "voice": {
                    "provider": "11labs",  # Usamos 11Labs para la voz
                    "voiceId": "JYyJjNPfmNJdaby8LdZs", # ID de voz de 11Labs
                    "speed": 1.11       # Velocidad de la voz
                },
                
                "firstMessage": personalized_first_message,
                "endCallPhrases": ["adios", "hasta luego", "bye", "tengo que colgar", "eso es todo"],
                "silenceTimeoutSeconds": 10, # Activa la regla del prompt tras 3s de silencio
                "responseDelaySeconds": 0.0, # Tiempo de espera antes de responder (en segundos)

                #PARÁMETRO PARA DETECTAR BUZÓN DE VOZ
                #"voicemailDetection": {
                #  "voicemailMessage": personalized_voicemail
                #},
                "model": {
                    "provider": "openai",   # Usamos OpenAI para el modelo de IA
                    "model": "gpt-4o-mini",   # Modelo de IA
                    "temperature": 0.9,      # Controla la creatividad de las respuestas
                    "maxTokens": 1500,       # Máximo de tokens por respuesta                   
                    "systemPrompt": personalized_prompt
                }
            }
        }
        
        try:
            response = requests.post(url, headers=self.vapi_headers, json=call_data)
            response.raise_for_status()
            call_info = response.json()
            logger.info(f"Llamada creada exitosamente para {customer_name} ({phone_number})")
            return call_info
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al crear llamada VAPI para {phone_number}: {e}")
            if e.response is not None:
                logger.error(f"Respuesta de la API: {e.response.text}")
            return None

    def get_call_status(self, call_id: str) -> Optional[Dict]:
        """
        Obtiene el estado de una llamada específica de la API de VAPI.
        """
        url = f"{self.vapi_base_url}/call/{call_id}"
        try:
            response = requests.get(url, headers=self.vapi_headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener estado de llamada {call_id}: {e}")
            return None

    def process_single_contact(self, contact: pd.Series) -> Dict:
        """
        Procesa un contacto individual para realizar una llamada. No modifica el Excel.
        """
        call_result = self.create_vapi_call(contact)
        
        if call_result:
            return {
                'success': True,
                'call_id': call_result.get('id'),
                'status': call_result.get('status', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': 'Error al crear la llamada en la API de VAPI',
                'call_id': None
            }

    def call_single_contact(self, contact: pd.Series, index: int) -> bool:
        """
        Procesa un solo contacto seleccionado y actualiza el Excel inmediatamente.
        """
        logger.info(f"Iniciando llamada individual a: {contact.get(self.col_name, 'N/A')}")
        result = self.process_single_contact(contact)
        
        df = self.load_contacts_from_excel()
        if index >= len(df):
            logger.error(f"Índice {index} fuera de rango para el DataFrame.")
            return False

        # Asegurarse de que las columnas de tracking existan antes de asignarles valores
        for col in self.config['excel_columns']['tracking']:
            if col not in df.columns:
                df[col] = None # O pd.NA, o '' dependiendo de lo que prefieras

        df.loc[index, 'call_success'] = result['success']
        df.loc[index, 'call_timestamp'] = result.get('timestamp', '')
        
        if result['success']:
            df.loc[index, 'call_id'] = result['call_id']
            df.loc[index, 'call_status'] = result['status']
            logger.info(f"Llamada individual exitosa - ID: {result['call_id']}")
        else:
            df.loc[index, 'call_id'] = ''
            df.loc[index, 'call_status'] = f"Error: {result.get('error', 'Unknown')}"
            logger.error(f"Error en llamada individual: {result.get('error', 'Unknown')}")
        
        self.save_contacts_to_excel(df)
        return result['success']

    def process_all_contacts(self):
        """
        Procesa todos los contactos del Excel en un bucle.
        """
        delay = self.config['call_settings']['delay_between_calls']
        df = self.load_contacts_from_excel()
        
        if df.empty:
            logger.error("No hay contactos para procesar")
            return
        
        for col in self.config['excel_columns']['tracking']:
            if col not in df.columns:
                df[col] = ''
        
        total_contacts = len(df)
        processed_count = 0
        
        logger.info(f"Iniciando procesamiento de {total_contacts} contactos.")
        
        for index, contact in df.iterrows():
            if contact.get('call_success') == True:
                logger.info(f"Contacto {contact.get(self.col_name, 'N/A')} ya procesado, saltando...")
                continue
            
            logger.info(f"Procesando contacto {processed_count + 1}/{total_contacts}: {contact.get(self.col_name, 'N/A')}")
            
            result = self.process_single_contact(contact)
            
            df.loc[index, 'call_success'] = result['success']
            df.loc[index, 'call_timestamp'] = result.get('timestamp', '')
            df.loc[index, 'call_id'] = result.get('call_id', '')
            df.loc[index, 'call_status'] = result.get('status') if result['success'] else f"Error: {result.get('error', 'Unknown')}"
            
            processed_count += 1
            
            if processed_count % 5 == 0:
                self.save_contacts_to_excel(df)
            
            if processed_count < total_contacts:
                logger.info(f"Esperando {delay} segundos...")
                time.sleep(delay)
        
        self.save_contacts_to_excel(df)
        logger.info("PROCESAMIENTO COMPLETADO")

    def check_calls_status(self):
        """
        Verifica y actualiza el estado de las llamadas. Si una llamada ha terminado,
        extrae su transcripción, duración y resumen, y los guarda en el Excel.
        """

        df = self.load_contacts_from_excel()
        # Aseguramos que todas las columnas de seguimiento existan
        for col in self.config['excel_columns']['tracking']:
            if col not in df.columns:
                df[col] = ''

        calls_to_check = df[df['call_id'].notna() & (df['call_id'] != '')]
        
        if calls_to_check.empty:
            print("\n>> No hay llamadas con ID para verificar.")
            return

        print(f"\nVerificando estado de {len(calls_to_check)} llamadas...")
        
        updated_count = 0
        for index, row in calls_to_check.iterrows():
            call_id = row['call_id']
            # Solo revisamos llamadas que no tengan ya una transcripción para ser eficientes
            if row.get('call_status') == 'ended' and row.get('call_transcript', '') != '':
                continue

            status_info = self.get_call_status(call_id)
            if status_info:
                current_status = status_info.get('status', 'unknown')
                
                if row['call_status'] != current_status:
                    df.loc[index, 'call_status'] = current_status
                    print(f"  Llamada para {row.get(self.col_name, 'N/A')} ({call_id[:8]}...): {current_status}")
                    updated_count += 1
                
                if current_status == 'ended':
                    
                    # 1. Extraer Transcripción
                    transcript = status_info.get('transcript', 'No disponible.')
                    df.loc[index, 'call_transcript'] = transcript
                    
                    # 2. Calcular Duración
                    duration_seconds = 0
                    if status_info.get('startedAt') and status_info.get('endedAt'):
                        # Convertimos las fechas de texto a objetos de fecha
                        start_time = datetime.fromisoformat(status_info['startedAt'].replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(status_info['endedAt'].replace('Z', '+00:00'))
                        # Calculamos la diferencia
                        duration = end_time - start_time
                        duration_seconds = int(duration.total_seconds())
                    
                    df.loc[index, 'call_duration'] = f"{duration_seconds} segundos"
                    
                    print(f" Datos guardados (Transcripción y Duración).")
            else:
                logger.warning(f"No se pudo obtener estado de llamada {call_id}")
        
        self.save_contacts_to_excel(df)
        
        if updated_count > 0:
            print(f"\n>> Verificación completada. Se actualizaron {updated_count} registros.")
        else:
            print("\n>> Verificación completada. No se encontraron nuevos cambios de estado.")