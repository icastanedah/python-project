import requests
import json
import os

def analyze_image(image_path, latitude=None, longitude=None):
    """
    Envía una imagen a la API para su análisis
    
    Args:
        image_path (str): Ruta al archivo de imagen
        latitude (float, optional): Latitud
        longitude (float, optional): Longitud
        
    Returns:
        dict: Resultados del análisis
    """
    # URL de la API
    url = "http://localhost:8080/api/analyze"
    
    # Preparar los datos
    files = {'image': open(image_path, 'rb')}
    data = {}
    
    # Agregar coordenadas si están disponibles
    if latitude is not None and longitude is not None:
        data['latitude'] = latitude
        data['longitude'] = longitude
    
    # Enviar la petición
    response = requests.post(url, files=files, data=data)
    
    # Verificar si la petición fue exitosa
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # Ruta a la imagen que quieres analizar
    image_path = "ruta/a/tu/imagen.jpg"
    
    # Coordenadas GPS (opcional)
    latitude = 19.4326
    longitude = -99.1332
    
    # Analizar la imagen
    results = analyze_image(image_path, latitude, longitude)
    
    # Mostrar los resultados
    if results:
        print(json.dumps(results, indent=2)) 