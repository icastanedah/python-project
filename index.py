from flask import Flask, request, jsonify, render_template, redirect
import os
import sys
import json
import datetime
import base64
from flask_cors import CORS

# Configurar credenciales de Google Cloud desde variables de entorno
if os.environ.get('GOOGLE_CREDENTIALS_BASE64'):
    # Decodificar las credenciales en base64 y guardarlas en un archivo temporal
    credentials_json = base64.b64decode(os.environ.get('GOOGLE_CREDENTIALS_BASE64')).decode('utf-8')
    credentials_path = 'vision-api-credentials.json'
    with open(credentials_path, 'w') as f:
        f.write(credentials_json)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

# Importar módulos necesarios
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from app.api.vision_api import analyze_image
    from app.api.maps_api import get_location_info
    from app.utils.image_utils import save_uploaded_image, allowed_file
except ImportError:
    # Si estamos ejecutando desde dentro del directorio app
    from api.vision_api import analyze_image
    from api.maps_api import get_location_info
    from utils.image_utils import save_uploaded_image, allowed_file

app = Flask(__name__)
CORS(app)

# Configuración
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Asegurar que el directorio de uploads exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html', maps_api_key=app.config['MAPS_API_KEY'])

@app.route('/api/health')
def health():
    """Endpoint para verificar el estado de la API"""
    return jsonify({"status": "ok"})

@app.route('/api/process_complete', methods=['POST'])
def process_complete():
    """
    Endpoint para procesar imágenes de incidentes y tarjetas de circulación,
    y enviar la información completa al sistema de boletas.
    """
    result = {
        'success': False,
        'incident_analysis': None,
        'registration_info': None,
        'location_info': None,
        'timestamp': datetime.datetime.now().isoformat(),
        'errors': []
    }
    
    try:
        # Procesar imagen del incidente
        if 'incident_image' not in request.files:
            app.logger.error("No se envió ninguna imagen de incidente")
            result['errors'].append('No se envió ninguna imagen de incidente')
            return jsonify(result), 400
        
        incident_file = request.files['incident_image']
        
        # Verificar si el archivo tiene nombre
        if incident_file.filename == '':
            app.logger.error("No se seleccionó ningún archivo para el incidente")
            result['errors'].append('No se seleccionó ningún archivo para el incidente')
            return jsonify(result), 400
        
        # Verificar si el archivo es una imagen permitida
        if not allowed_file(incident_file.filename):
            app.logger.error(f"Formato de archivo no permitido para incidente: {incident_file.filename}")
            result['errors'].append('Formato de archivo no permitido para incidente. Use JPG, PNG, JPEG o GIF')
            return jsonify(result), 400
        
        # Guardar la imagen del incidente
        app.logger.info(f"Guardando imagen de incidente: {incident_file.filename}")
        incident_image_path = save_uploaded_image(incident_file, app.config['UPLOAD_FOLDER'])
        app.logger.info(f"Imagen de incidente guardada en: {incident_image_path}")
        
        # Analizar la imagen con Google Cloud Vision
        app.logger.info(f"Analizando imagen de incidente con Vision API: {incident_image_path}")
        incident_analysis = analyze_image(incident_image_path)
        
        # Verificar si el análisis fue exitoso
        if incident_analysis is None or 'error' in incident_analysis:
            error_msg = incident_analysis.get('error', 'Error desconocido al analizar la imagen') if incident_analysis else 'No se pudo analizar la imagen'
            app.logger.error(f"Error en el análisis de incidente: {error_msg}")
            result['errors'].append(f"Error en el análisis de incidente: {error_msg}")
            # Proporcionar un análisis básico para evitar errores en el frontend
            incident_analysis = {
                'incident_type': 'Error en el análisis',
                'damage_severity': 'Desconocido',
                'vehicle_type': 'Desconocido',
                'damaged_parts': [],
                'confidence': 0.0,
                'error': error_msg
            }
        
        result['incident_analysis'] = incident_analysis
        
        # Procesar imagen de tarjeta de circulación si se proporcionó
        registration_info = None
        if 'registration_image' in request.files and request.files['registration_image'].filename != '':
            registration_file = request.files['registration_image']
            
            # Verificar si el archivo es una imagen permitida
            if not allowed_file(registration_file.filename):
                app.logger.error(f"Formato de archivo no permitido para tarjeta: {registration_file.filename}")
                result['errors'].append('Formato de archivo no permitido para tarjeta. Use JPG, PNG, JPEG o GIF')
            else:
                # Guardar la imagen de la tarjeta
                app.logger.info(f"Guardando imagen de tarjeta: {registration_file.filename}")
                registration_image_path = save_uploaded_image(registration_file, app.config['UPLOAD_FOLDER'])
                app.logger.info(f"Imagen de tarjeta guardada en: {registration_image_path}")
                
                # Analizar la imagen de la tarjeta
                app.logger.info(f"Analizando imagen de tarjeta con Vision API: {registration_image_path}")
                registration_analysis = analyze_image(registration_image_path, is_registration_card=True)
                
                if 'registration_info' in registration_analysis:
                    registration_info = registration_analysis['registration_info']
                    result['registration_info'] = registration_info
                else:
                    app.logger.error("No se pudo extraer información de la tarjeta de circulación")
                    result['errors'].append('No se pudo extraer información de la tarjeta de circulación')
        
        # Alternativamente, usar datos de registro proporcionados directamente en JSON
        elif 'registration_data' in request.form:
            try:
                registration_info = json.loads(request.form['registration_data'])
                result['registration_info'] = registration_info
            except json.JSONDecodeError:
                app.logger.error("Error al decodificar los datos de registro JSON")
                result['errors'].append('Error al decodificar los datos de registro JSON')
        
        # Obtener datos de ubicación (si se proporcionaron)
        location_data = {}
        if 'latitude' in request.form and 'longitude' in request.form:
            try:
                latitude = float(request.form['latitude'])
                longitude = float(request.form['longitude'])
                app.logger.info(f"Obteniendo información de ubicación: {latitude}, {longitude}")
                
                # Verificar si la API key de Google Maps está configurada
                if not app.config['MAPS_API_KEY']:
                    app.logger.warning("API key de Google Maps no configurada. Usando ubicación sin geocodificación.")
                    location_data = {
                        'coordinates': {
                            'latitude': latitude,
                            'longitude': longitude
                        },
                        'address': f"Coordenadas: {latitude}, {longitude}",
                        'city': 'No disponible',
                        'country': 'No disponible'
                    }
                else:
                    # Intentar obtener información de ubicación
                    try:
                        location_data = get_location_info(latitude, longitude)
                    except Exception as loc_error:
                        app.logger.error(f"Error al obtener información de ubicación: {str(loc_error)}")
                        location_data = {
                            'error': f"Error al obtener información de ubicación: {str(loc_error)}",
                            'coordinates': {
                                'latitude': latitude,
                                'longitude': longitude
                            },
                            'address': f"Coordenadas: {latitude}, {longitude}",
                            'city': 'No disponible',
                            'country': 'No disponible'
                        }
                
                result['location_info'] = location_data
            except (ValueError, KeyError) as e:
                app.logger.warning(f"Error al procesar coordenadas: {str(e)}")
                # Si hay error en las coordenadas, continuamos sin datos de ubicación
                location_data = {
                    'error': 'Coordenadas inválidas',
                    'coordinates': {
                        'latitude': request.form.get('latitude', 'inválido'),
                        'longitude': request.form.get('longitude', 'inválido')
                    },
                    'address': 'Coordenadas inválidas',
                    'city': 'No disponible',
                    'country': 'No disponible'
                }
                result['location_info'] = location_data
                result['errors'].append('Error al procesar coordenadas')
        
        # Preparar el paquete completo para enviar al sistema de boletas
        ticket_data = {
            'incident': incident_analysis,
            'vehicle': registration_info,
            'location': location_data,
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Aquí se podría implementar el envío al sistema de boletas
        # Por ahora, solo lo incluimos en la respuesta
        result['ticket_data'] = ticket_data
        result['success'] = True
        
        # Añadir las URLs de las imágenes para mostrarlas en el frontend
        if 'incident_image_path' in locals():
            incident_image_url = incident_image_path.replace('\\', '/').replace(app.config['UPLOAD_FOLDER'], '/static/uploads')
            result['incident_image_url'] = incident_image_url
        
        if 'registration_image_path' in locals():
            registration_image_url = registration_image_path.replace('\\', '/').replace(app.config['UPLOAD_FOLDER'], '/static/uploads')
            result['registration_image_url'] = registration_image_url
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error al procesar la solicitud completa: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        result['errors'].append(f"Error al procesar la solicitud: {str(e)}")
        return jsonify(result), 500

# Para pruebas locales
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) 