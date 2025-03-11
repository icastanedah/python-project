#!/bin/bash

# Ruta a la imagen que quieres analizar
IMAGE_PATH="ruta/a/tu/imagen.jpg"

# Coordenadas GPS (opcional)
LATITUDE="19.4326"
LONGITUDE="-99.1332"

# Enviar la petición a la API
curl -X POST \
  -F "image=@$IMAGE_PATH" \
  -F "latitude=$LATITUDE" \
  -F "longitude=$LONGITUDE" \
  http://localhost:8080/api/analyze 