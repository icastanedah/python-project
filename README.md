# API de Análisis de Imágenes para Siniestros Vehiculares

Esta API utiliza inteligencia artificial de Google Cloud Vision para analizar imágenes de siniestros vehiculares y determinar el tipo de siniestro y la ubicación donde ocurrió.

## Características

- Análisis de imágenes para detectar daños en vehículos
- Clasificación del tipo de siniestro
- Determinación de la ubicación mediante análisis de imágenes y datos GPS
- Interfaz para subir imágenes y recibir análisis

## Tecnologías utilizadas

- Python 3.9+
- Flask (Framework web)
- Google Cloud Vision API (Análisis de imágenes)
- Google Maps API (Geolocalización)

## Configuración

### Requisitos previos

- Cuenta de Google Cloud Platform con APIs habilitadas:
  - Google Cloud Vision API
  - Google Maps Platform API

### Instalación

1. Clonar el repositorio:
```
git clone https://github.com/tu-usuario/recognize-images.git
cd recognize-images
```

2. Instalar dependencias:
```
pip install -r requirements.txt
```

3. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
GOOGLE_APPLICATION_CREDENTIALS=ruta/a/tu/archivo-credenciales.json
GOOGLE_MAPS_API_KEY=tu_clave_api_de_google_maps
```

4. Ejecutar la aplicación:
```
python app/app.py
```

## Uso de la API

### Endpoints

- `POST /api/analyze`: Analiza una imagen de siniestro vehicular
  - Parámetros:
    - `image`: Archivo de imagen (JPG, PNG)
    - `location`: Coordenadas GPS (opcional)

### Ejemplo de respuesta

```json
{
  "analysis": {
    "incident_type": "Colisión lateral",
    "damage_severity": "Moderado",
    "vehicle_type": "Sedán",
    "damaged_parts": ["Puerta delantera izquierda", "Guardabarros"]
  },
  "location": {
    "address": "Av. Principal 123, Ciudad",
    "coordinates": {
      "latitude": 19.4326,
      "longitude": -99.1332
    }
  }
}
```

## Limitaciones

- La precisión del análisis depende de la calidad de las imágenes proporcionadas
- Se requiere conexión a internet para utilizar las APIs de Google Cloud 