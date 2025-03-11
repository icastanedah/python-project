#!/usr/bin/env python3
"""
Script para probar el envío de datos directamente a la API externa.
Este script envía datos de prueba al endpoint /api/send-to-external de la aplicación principal.
"""

import json
import requests
import sys
import os

def send_data(data, api_url=None):
    """
    Envía datos a la API externa a través del endpoint de la aplicación principal.
    
    Args:
        data (dict): Datos a enviar
        api_url (str, optional): URL de la API externa. Si no se proporciona, se usará la URL por defecto.
    
    Returns:
        dict: Respuesta de la API
    """
    # URL de la aplicación principal
    app_url = "http://localhost:8080/api/send-to-external"
    
    # Añadir parámetro de URL de la API externa si se proporcionó
    if api_url:
        app_url += f"?api_url={api_url}"
    
    print(f"Enviando datos a: {app_url}")
    print("Datos a enviar:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    try:
        # Enviar solicitud POST
        response = requests.post(
            app_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10  # Timeout de 10 segundos
        )
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            print("Datos enviados exitosamente")
            print("Respuesta:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return response.json()
        else:
            print(f"Error al enviar datos. Código: {response.status_code}")
            print("Respuesta:")
            print(response.text)
            return {
                'success': False,
                'status_code': response.status_code,
                'error': response.text
            }
    except requests.RequestException as e:
        print(f"Error de conexión: {str(e)}")
        return {
            'success': False,
            'error': f"Error de conexión: {str(e)}"
        }
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {
            'success': False,
            'error': f"Error inesperado: {str(e)}"
        }

def main():
    """Función principal"""
    # Datos de prueba
    test_data = {
        'incident': {
            'incident_type': 'Fallo mecánico - Llanta pinchada',
            'damage_severity': 'Moderado',
            'vehicle_type': 'Automóvil',
            'damaged_parts': ['Llanta', 'Neumático'],
            'confidence': 95.0
        },
        'vehicle': {
            'placa': 'ABC123',
            'nombre_propietario': 'Juan Pérez',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'año': '2020',
            'color': 'Blanco'
        },
        'location': {
            'coordinates': {
                'latitude': 14.529358,
                'longitude': -90.606279
            },
            'address': 'Ciudad de Guatemala, Guatemala',
            'city': 'Ciudad de Guatemala',
            'country': 'Guatemala'
        },
        'timestamp': '2023-03-11T00:00:00.000Z',
        'status': 'pending'
    }
    
    # Obtener URL de la API externa de los argumentos de línea de comandos
    api_url = None
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    # Enviar datos
    send_data(test_data, api_url)

if __name__ == '__main__':
    main() 