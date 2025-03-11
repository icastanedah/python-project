# Guía para probar la funcionalidad de API Externa

Esta guía te ayudará a probar la funcionalidad de envío de datos a una API externa que hemos implementado en la aplicación de reconocimiento de imágenes.

## Estructura de los datos enviados

Cuando la aplicación envía datos a una API externa, utiliza la siguiente estructura JSON:

```json
{
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
  "timestamp": "2023-11-15T14:30:45",
  "status": "pending"
}
```

## Opciones para probar la funcionalidad

Hay varias formas de probar esta funcionalidad:

### 1. Usando el servidor de prueba incluido

Hemos creado un servidor de prueba simple que puede recibir los datos enviados por la aplicación principal.

#### Pasos:

1. Inicia el servidor de prueba:
   ```bash
   python test_api_server.py
   ```
   Esto iniciará un servidor en http://localhost:5001/receive_data

2. En otra terminal, ejecuta la aplicación principal:
   ```bash
   ./start.sh
   ```

3. Accede a la aplicación en tu navegador (http://localhost:8082)

4. Procesa una imagen de incidente y una tarjeta de circulación

5. Marca la casilla "Enviar datos a API externa" e ingresa la URL:
   ```
   http://localhost:5001/receive_data
   ```

6. Completa el proceso y envía los datos

7. Verifica en la terminal donde ejecutaste el servidor de prueba que los datos se recibieron correctamente

### 2. Usando el simulador de envío

También puedes usar el script de simulación para ver exactamente qué datos se enviarían:

```bash
python test_send_data.py
```

Este script enviará datos de ejemplo al servidor de prueba y mostrará tanto los datos enviados como la respuesta recibida.

### 3. Usando curl para probar manualmente

Si prefieres usar curl, puedes ejecutar el siguiente comando:

```bash
curl -X POST "http://localhost:5001/receive_data" \
  -H "Content-Type: application/json" \
  -d '{
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
  "timestamp": "2023-11-15T14:30:45",
  "status": "pending"
}'
```

## Integrando con tu propia API

Para integrar con tu propia API, necesitas:

1. Asegurarte de que tu API pueda recibir solicitudes POST con datos JSON
2. Configurar tu API para procesar la estructura de datos mostrada arriba
3. En la aplicación principal, marca la casilla "Enviar datos a API externa" e ingresa la URL de tu API

## Solución de problemas

- **Error de conexión**: Asegúrate de que el servidor de la API externa esté en ejecución y sea accesible
- **Error de formato**: Verifica que tu API pueda procesar el formato JSON enviado
- **Timeout**: Si la API tarda demasiado en responder, ajusta el timeout en la configuración

Si tienes alguna pregunta o problema, no dudes en contactarnos. 