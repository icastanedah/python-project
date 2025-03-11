import os
import requests
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la API key de Google Maps desde variables de entorno
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

def get_location_info(latitude, longitude):
    """
    Obtiene información de ubicación a partir de coordenadas GPS
    utilizando Google Maps Geocoding API
    
    Args:
        latitude (float): Latitud
        longitude (float): Longitud
        
    Returns:
        dict: Información de la ubicación
    """
    if not GOOGLE_MAPS_API_KEY:
        logger.warning("No se ha configurado la API key de Google Maps")
        return {
            'error': 'No se ha configurado la API key de Google Maps',
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            },
            'address': f"Coordenadas: {latitude}, {longitude}",
            'city': 'No disponible',
            'country': 'No disponible'
        }
    
    try:
        # Construir URL para la solicitud a Geocoding API
        geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={GOOGLE_MAPS_API_KEY}"
        
        # Realizar solicitud
        response = requests.get(geocoding_url)
        data = response.json()
        
        # Verificar si la solicitud fue exitosa
        if data['status'] != 'OK':
            error_message = f"Error en la solicitud a Geocoding API: {data['status']}"
            if data['status'] == 'REQUEST_DENIED':
                error_message += ". Posible problema con la API key o restricciones de la API."
                logger.error(f"{error_message} Verifica que la API key sea válida y que la API de Geocoding esté habilitada en la consola de Google Cloud.")
                logger.error("Pasos para habilitar la API de Geocoding:")
                logger.error("1. Ve a https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com")
                logger.error("2. Selecciona tu proyecto")
                logger.error("3. Haz clic en 'Habilitar'")
                logger.error("4. Verifica que la API key tenga los permisos necesarios en https://console.cloud.google.com/apis/credentials")
            else:
                logger.error(error_message)
            
            # Proporcionar una ubicación por defecto con las coordenadas
            return {
                'error': error_message,
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'address': f"Coordenadas: {latitude}, {longitude}",
                'city': 'No disponible',
                'country': 'No disponible'
            }
        
        # Procesar resultados
        location_data = {
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            },
            'address': data['results'][0]['formatted_address'] if data['results'] else f"Coordenadas: {latitude}, {longitude}",
            'components': {},
            'city': 'No disponible',
            'country': 'No disponible'
        }
        
        # Extraer componentes de la dirección
        if data['results'] and 'address_components' in data['results'][0]:
            for component in data['results'][0]['address_components']:
                for type in component['types']:
                    location_data['components'][type] = component['long_name']
                    
                    # Extraer ciudad y país para facilitar el acceso
                    if type == 'locality' or type == 'administrative_area_level_1':
                        location_data['city'] = component['long_name']
                    elif type == 'country':
                        location_data['country'] = component['long_name']
        
        return location_data
    
    except Exception as e:
        logger.error(f"Error al obtener información de ubicación: {str(e)}")
        # Proporcionar una ubicación por defecto con las coordenadas
        return {
            'error': f"Error al obtener información de ubicación: {str(e)}",
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            },
            'address': f"Coordenadas: {latitude}, {longitude}",
            'city': 'No disponible',
            'country': 'No disponible'
        }

def get_nearby_places(latitude, longitude, place_type='hospital', radius=5000):
    """
    Obtiene lugares cercanos a las coordenadas dadas
    utilizando Google Places API
    
    Args:
        latitude (float): Latitud
        longitude (float): Longitud
        place_type (str): Tipo de lugar a buscar (hospital, police, etc.)
        radius (int): Radio de búsqueda en metros
        
    Returns:
        list: Lista de lugares cercanos
    """
    if not GOOGLE_MAPS_API_KEY:
        logger.warning("No se ha configurado la API key de Google Maps")
        return []
    
    try:
        # Construir URL para la solicitud a Places API
        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={radius}&type={place_type}&key={GOOGLE_MAPS_API_KEY}"
        
        # Realizar solicitud
        response = requests.get(places_url)
        data = response.json()
        
        # Verificar si la solicitud fue exitosa
        if data['status'] != 'OK' and data['status'] != 'ZERO_RESULTS':
            logger.error(f"Error en la solicitud a Places API: {data['status']}")
            return []
        
        # Procesar resultados
        places = []
        for place in data.get('results', []):
            places.append({
                'name': place.get('name', 'Sin nombre'),
                'vicinity': place.get('vicinity', 'Sin dirección'),
                'location': {
                    'latitude': place['geometry']['location']['lat'],
                    'longitude': place['geometry']['location']['lng']
                },
                'types': place.get('types', []),
                'rating': place.get('rating', 0)
            })
        
        return places
    
    except Exception as e:
        logger.error(f"Error al obtener lugares cercanos: {str(e)}")
        return [] 