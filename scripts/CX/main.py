# main.py

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from config import CONFIG
from sistema_de_encuestas import SurveyCallSystem

def setup_logging():
    """Configura el sistema de logging para que escriba a un archivo y a la consola."""
    log_file = CONFIG['logging']['file_path']
    log_level = CONFIG['logging']['level']
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging configurado.")

def call_specific_contact(survey_system: SurveyCallSystem):
    """Permite al usuario seleccionar y llamar a un contacto específico del archivo Excel."""
    try:
        df = survey_system.load_contacts_from_excel()
        if df.empty:
            print("\nNo hay contactos en el archivo Excel.")
            return

        col_name = CONFIG['excel_columns']['mapping']['name']
        col_phone = CONFIG['excel_columns']['mapping']['phone']

        print("\n--- Contactos Disponibles ---")
        for idx, row in df.iterrows():
            nombre_a_mostrar = str(row.get(col_name, 'COLUMNA NO ENCONTRADA'))
            telefono_a_mostrar = str(row.get(col_phone, 'N/A'))
            estado_a_mostrar = str(row.get('call_status', 'Pendiente'))
            print(f"  {idx + 1:<3} | {nombre_a_mostrar:<25.25} | {telefono_a_mostrar:<15.15} | {estado_a_mostrar:<20.20}")
        
        while True:
            try:
                selection = input(f"\nSelecciona el número del contacto a llamar (1-{len(df)}) o 'q' para cancelar: ").strip()
                if selection.lower() == 'q':
                    print(">> Operación cancelada.")
                    return
                
                contact_idx = int(selection) - 1
                if 0 <= contact_idx < len(df):
                    selected_contact = df.iloc[contact_idx]
                    break
                else:
                    print(f"Error: Por favor ingresa un número entre 1 y {len(df)}.")
            except ValueError:
                print("Error: Por favor ingresa un número válido.")
        
        confirm = input(f"\n¿Confirmas la llamada a {selected_contact[col_name]}? (s/n): ").lower()
        if confirm == 's':
            print(f"\nIniciando llamada...")
            success = survey_system.call_single_contact(selected_contact, contact_idx)
            print(">> Llamada exitosa." if success else ">> Error al realizar la llamada.")
        else:
            print(">> Llamada cancelada.")
    
    except Exception as e:
        logging.error(f"Error en call_specific_contact: {e}")
        print(f"\nError inesperado: {e}")

def show_statistics(survey_system: SurveyCallSystem):
    """Muestra estadísticas basadas en el archivo Excel."""
    df = survey_system.load_contacts_from_excel()
    if df.empty:
        print("\n>> No hay datos para mostrar estadísticas.")
        return
        
    total = len(df)
    success = len(df[df['call_success'] == True]) if 'call_success' in df.columns else 0
    failed = len(df[df['call_success'] == False]) if 'call_success' in df.columns else 0
    pending = total - success - failed
    
    print("\n--- Estadísticas Actuales ---")
    print(f"  Total de contactos: {total}")
    print(f"  Llamadas exitosas: {success}")
    print(f"  Llamadas fallidas: {failed}")
    print(f"  Llamadas pendientes: {pending}")

def main():
    """Función principal que ejecuta el menú de la aplicación."""
    setup_logging()
    
    print("\n" + "="*50)
    print("   SISTEMA DE ENCUESTAS TELEFÓNICAS AUTOMATIZADO")
    print("="*50)

    #Se pasa el objeto CONFIG importado al inicializar el sistema.
    survey_system = SurveyCallSystem(CONFIG)
    
    #Se usa un diccionario (dispatcher) para un menú más limpio y escalable.
    menu_actions = {
        '1': survey_system.process_all_contacts,
        '2': lambda: call_specific_contact(survey_system),
        '3': survey_system.check_calls_status,
        '4': lambda: show_statistics(survey_system),
    }
    #while True:
    print("\n--- Menú Principal ---")
    print("1. Procesar todos los contactos")
    print("2. Llamar a un contacto específico")
    print("3. Verificar estado de llamadas")
    print("4. Ver estadísticas")

        
    choice = input("\nSelecciona una opción: ").strip()
        
    
    action = menu_actions.get(choice)
    if action:
        try:
            action()
        except Exception as e:
            logging.error(f"Error ejecutando la opción '{choice}': {e}")
            print(f"\nError inesperado: {e}")
    else:
        print("Opción no válida. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    main()