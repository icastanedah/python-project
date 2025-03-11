import requests
import json
from datetime import datetime

# URL de la API externa (el servidor de prueba que acabamos de crear)
API_URL = "http://localhost:5001/receive_data"

# Datos de ejemplo que simulan lo que enviaría tu aplicación principal
sample_data = {
    "incident": {
        "incident_type": "Fallo mecánico - Llanta pinchada",
        "damage_severity": "Moderado",
        "vehicle_type": "Automóvil",
        "damaged_parts": ["Llanta", "Neumático"],
        "confidence": 95.0,
        "description": "Vehículo con llanta pinchada en el lado derecho"
    },
    "vehicle": {
        "placa": "ABC123",
        "nombre_propietario": "Juan Pérez",
        "marca": "Toyota",
        "modelo": "Corolla",
        "año": "2020",
        "color": "Blanco",
        "tipo": "Automóvil"
    },
    "location": {
        "coordinates": {
            "latitude": 14.529358,
            "longitude": -90.606278
        },
        "address": "Avenida Principal 123, Zona 10",
        "city": "Ciudad de Guatemala",
        "country": "Guatemala"
    },
    "timestamp": datetime.now().isoformat(),
    "status": "pending"
}

def send_test_data():
    """
    Envía datos de prueba a la API externa y muestra la respuesta
    """
    print("Enviando datos de prueba a:", API_URL)
    print("\nDatos que se enviarán:")
    print(json.dumps(sample_data, indent=2))
    
    try:
        # Realizar la solicitud POST a la API externa
        response = requests.post(
            API_URL,
            json=sample_data,
            headers={'Content-Type': 'application/json'},
            timeout=10  # Timeout de 10 segundos
        )
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            print("\n✅ Datos enviados exitosamente")
            print("Respuesta recibida:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ Error al enviar datos. Código: {response.status_code}")
            print("Respuesta de error:")
            print(response.text)
    
    except Exception as e:
        print(f"\n❌ Error en la solicitud: {str(e)}")

if __name__ == "__main__":
    print("=== SIMULADOR DE ENVÍO DE DATOS A API EXTERNA ===")
    print("Este script simula el envío de datos desde tu aplicación principal a una API externa")
    print("Asegúrate de que el servidor de prueba (test_api_server.py) esté en ejecución")
    
    # Preguntar al usuario si desea continuar
    input("Presiona Enter para enviar los datos de prueba...")
    
    # Enviar los datos
    send_test_data() 