import json
from flask import Blueprint, request, jsonify
import datetime
import uuid

# Crear un Blueprint para la API de Angular
angular_api = Blueprint('angular_api', __name__)

# Almacenamiento temporal para los datos recibidos (en una aplicación real usarías una base de datos)
received_incidents = []

def receive_data_internal(data):
    """
    Función para recibir datos internamente sin pasar por HTTP
    
    Args:
        data (dict): Datos del siniestro
        
    Returns:
        dict: Respuesta con el ID del incidente
    """
    try:
        # Validar que contenga la información mínima necesaria
        required_sections = ['incident', 'vehicle', 'location']
        for section in required_sections:
            if section not in data:
                return {
                    'success': False,
                    'error': f'Falta la sección {section}'
                }
        
        # Convertir los datos al formato esperado por la API
        incident_data = {
            'incident_info': {
                'description': data.get('incident', {}).get('incident_type', 'Sin descripción'),
                'date': datetime.datetime.now().isoformat(),
                'damage_type': data.get('incident', {}).get('damaged_parts', ['Desconocido'])[0] if data.get('incident', {}).get('damaged_parts') else 'Desconocido',
                'severity': data.get('incident', {}).get('damage_severity', 'Desconocido')
            },
            'vehicle_info': {
                'make': data.get('vehicle', {}).get('marca_modelo', '').split(' ')[0] if data.get('vehicle', {}).get('marca_modelo') else '',
                'model': ' '.join(data.get('vehicle', {}).get('marca_modelo', '').split(' ')[1:]) if data.get('vehicle', {}).get('marca_modelo') else '',
                'year': data.get('vehicle', {}).get('año', ''),
                'plate': data.get('vehicle', {}).get('placa', ''),
                'color': data.get('vehicle', {}).get('color', '')
            },
            'location': data.get('location', {})
        }
        
        # Añadir timestamp y ID único
        incident_data['timestamp'] = datetime.datetime.now().isoformat()
        incident_data['incident_id'] = str(uuid.uuid4())
        incident_data['status'] = 'received'
        
        # Guardar los datos recibidos
        received_incidents.append(incident_data)
        
        return {
            'success': True,
            'message': 'Datos del siniestro recibidos correctamente',
            'incident_id': incident_data['incident_id']
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Error inesperado: {str(e)}"
        }

@angular_api.route('/receive', methods=['POST'])
def receive_data():
    """
    Endpoint para recibir datos completos de un siniestro
    
    Espera recibir:
    {
        "incident_info": {
            "description": "Descripción del siniestro",
            "date": "2025-03-11T08:00:00Z",
            "damage_type": "Frontal/Lateral/Trasero",
            "severity": "Leve/Moderado/Grave"
        },
        "vehicle_info": {
            "make": "Marca del vehículo",
            "model": "Modelo del vehículo",
            "year": "Año del vehículo",
            "plate": "Matrícula",
            "color": "Color del vehículo"
        },
        "insurance_info": {
            "policy_number": "Número de póliza",
            "card_number": "Número de tarjeta",
            "expiration_date": "Fecha de expiración",
            "holder_name": "Nombre del titular"
        },
        "location": {
            "latitude": 19.4326,
            "longitude": -99.1332,
            "address": "Dirección completa",
            "reference": "Punto de referencia"
        },
        "images": [
            {
                "url": "URL de la imagen",
                "type": "Tipo de imagen (daño, tarjeta, etc.)",
                "analysis_results": {}
            }
        ]
    }
    """
    try:
        # Verificar si se enviaron datos JSON
        if not request.is_json:
            return jsonify({'error': 'No se enviaron datos JSON'}), 400
        
        # Obtener los datos
        data = request.json
        
        # Validar que contenga la información mínima necesaria
        required_sections = ['incident_info', 'vehicle_info', 'location']
        for section in required_sections:
            if section not in data:
                return jsonify({'error': f'Falta la sección {section}'}), 400
        
        # Añadir timestamp y ID único
        incident = data.copy()
        incident['timestamp'] = datetime.datetime.now().isoformat()
        incident['incident_id'] = str(uuid.uuid4())
        incident['status'] = 'received'
        
        # Guardar los datos recibidos
        received_incidents.append(incident)
        
        return jsonify({
            'success': True,
            'message': 'Datos del siniestro recibidos correctamente',
            'incident_id': incident['incident_id']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error inesperado: {str(e)}"
        }), 500

@angular_api.route('/incidents', methods=['GET'])
def get_incidents():
    """
    Endpoint para obtener todos los siniestros recibidos
    """
    return jsonify({
        'success': True,
        'incidents': received_incidents
    })

@angular_api.route('/incidents/<incident_id>', methods=['GET'])
def get_incident_by_id(incident_id):
    """
    Endpoint para obtener un siniestro específico por su ID
    """
    try:
        for incident in received_incidents:
            if incident['incident_id'] == incident_id:
                return jsonify({
                    'success': True,
                    'incident': incident
                })
        
        return jsonify({
            'success': False,
            'error': 'ID de siniestro no encontrado'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error inesperado: {str(e)}"
        }), 500

@angular_api.route('/incidents/<incident_id>/status', methods=['PUT'])
def update_incident_status(incident_id):
    """
    Endpoint para actualizar el estado de un siniestro
    
    Espera recibir:
    {
        "status": "processing/approved/rejected/completed"
    }
    """
    try:
        # Verificar si se enviaron datos JSON
        if not request.is_json:
            return jsonify({'error': 'No se enviaron datos JSON'}), 400
        
        # Obtener los datos
        data = request.json
        
        # Validar que contenga el estado
        if 'status' not in data:
            return jsonify({'error': 'Falta el estado del siniestro'}), 400
        
        # Buscar el siniestro
        for incident in received_incidents:
            if incident['incident_id'] == incident_id:
                # Actualizar el estado
                incident['status'] = data['status']
                incident['status_updated_at'] = datetime.datetime.now().isoformat()
                
                return jsonify({
                    'success': True,
                    'message': 'Estado del siniestro actualizado correctamente',
                    'incident': incident
                })
        
        return jsonify({
            'success': False,
            'error': 'ID de siniestro no encontrado'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error inesperado: {str(e)}"
        }), 500

@angular_api.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Endpoint para obtener notificaciones de siniestros
    (Simulación - en una aplicación real esto podría usar websockets)
    """
    # Filtrar sólo los siniestros con cambios recientes (últimas 24 horas)
    recent_time = datetime.datetime.now() - datetime.timedelta(hours=24)
    recent_incidents = [
        {
            'incident_id': incident['incident_id'],
            'status': incident['status'],
            'timestamp': incident.get('status_updated_at', incident['timestamp']),
            'message': f"Siniestro {incident['incident_id']} actualizado a estado: {incident['status']}"
        }
        for incident in received_incidents
        if 'status_updated_at' in incident and datetime.datetime.fromisoformat(incident['status_updated_at']) > recent_time
    ]
    
    return jsonify({
        'success': True,
        'notifications': recent_incidents
    }) 