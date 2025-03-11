#!/usr/bin/env python3
"""
Script para probar un modelo de clasificación de imágenes desplegado en Vertex AI.
Este script:
1. Carga una imagen desde un archivo local
2. Envía la imagen al endpoint de Vertex AI para obtener predicciones
3. Muestra los resultados de la predicción
"""

import os
import argparse
import base64
from google.cloud import aiplatform
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def init_vertex_ai():
    """Inicializa Vertex AI con las credenciales adecuadas."""
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('GOOGLE_CLOUD_REGION', 'us-central1')
    
    if not project_id:
        raise ValueError("La variable de entorno GOOGLE_CLOUD_PROJECT no está configurada")
    
    aiplatform.init(project=project_id, location=location)
    print(f"Vertex AI inicializado para el proyecto: {project_id} en {location}")

def predict_image(image_path, endpoint_id=None, threshold=0.0):
    """
    Envía una imagen al endpoint de Vertex AI para obtener predicciones.
    
    Args:
        image_path (str): Ruta al archivo de imagen
        endpoint_id (str, opcional): ID del endpoint. Si no se proporciona, se usa VERTEX_ENDPOINT_ID
        threshold (float): Umbral de confianza mínimo para mostrar predicciones
        
    Returns:
        dict: Resultados de la predicción
    """
    # Obtener el ID del endpoint
    if not endpoint_id:
        endpoint_id = os.environ.get('VERTEX_ENDPOINT_ID')
        if not endpoint_id:
            raise ValueError("No se proporcionó un ID de endpoint y la variable VERTEX_ENDPOINT_ID no está configurada")
    
    # Cargar la imagen
    with open(image_path, "rb") as f:
        image_content = f.read()
    
    # Codificar la imagen en base64
    encoded_content = base64.b64encode(image_content).decode("utf-8")
    
    # Obtener el endpoint
    endpoint = aiplatform.Endpoint(endpoint_id)
    
    # Crear la instancia para la predicción
    instances = [{"content": encoded_content}]
    
    # Realizar la predicción
    print(f"Enviando imagen a Vertex AI para predicción: {image_path}")
    prediction = endpoint.predict(instances=instances)
    
    # Procesar los resultados
    results = []
    
    # El formato exacto de la respuesta puede variar según cómo se entrenó el modelo
    # Ajusta esta parte según sea necesario
    if hasattr(prediction, 'predictions') and prediction.predictions:
        pred = prediction.predictions[0]
        
        if 'displayNames' in pred and 'confidences' in pred:
            # Formato típico de AutoML Vision
            for label, score in zip(pred['displayNames'], pred['confidences']):
                if score >= threshold:
                    results.append({
                        'label': label,
                        'confidence': round(score * 100, 2)
                    })
        elif isinstance(pred, dict) and 'labels' in pred and 'scores' in pred:
            # Formato alternativo
            for label, score in zip(pred['labels'], pred['scores']):
                if score >= threshold:
                    results.append({
                        'label': label,
                        'confidence': round(score * 100, 2)
                    })
        else:
            # Si no podemos interpretar el formato, devolvemos la respuesta cruda
            print("Formato de respuesta no reconocido. Mostrando respuesta cruda:")
            print(prediction.predictions)
            return prediction.predictions
    
    # Ordenar por confianza
    results = sorted(results, key=lambda x: x['confidence'], reverse=True)
    return results

def main():
    parser = argparse.ArgumentParser(description='Probar un modelo de clasificación de imágenes en Vertex AI')
    parser.add_argument('--image', required=True, help='Ruta al archivo de imagen para predecir')
    parser.add_argument('--endpoint_id', help='ID del endpoint (opcional, por defecto usa VERTEX_ENDPOINT_ID)')
    parser.add_argument('--threshold', type=float, default=0.0, help='Umbral de confianza mínimo (0.0 a 1.0)')
    
    args = parser.parse_args()
    
    # Inicializar Vertex AI
    init_vertex_ai()
    
    # Realizar la predicción
    results = predict_image(args.image, args.endpoint_id, args.threshold)
    
    # Mostrar resultados
    print("\nResultados de la predicción:")
    print("-" * 50)
    
    if isinstance(results, list) and results:
        for i, result in enumerate(results):
            print(f"{i+1}. {result['label']}: {result['confidence']}%")
        
        # Mostrar la predicción principal
        top_prediction = results[0]
        print("\nPredicción principal:")
        print(f"Tipo de daño: {top_prediction['label']}")
        print(f"Confianza: {top_prediction['confidence']}%")
        
        # Mapear a categorías de la aplicación
        damage_type = "Desconocido"
        severity = "Desconocido"
        
        label = top_prediction['label']
        if "Batería" in label:
            damage_type = "Fallo mecánico - Batería"
            severity = "Moderado"
        elif "Llanta" in label:
            damage_type = "Fallo mecánico - Llanta pinchada"
            severity = "Moderado"
        elif "Fuga" in label or "Líquido" in label:
            damage_type = "Fallo mecánico - Fuga de líquido"
            severity = "Moderado"
        elif "Acceso" in label:
            damage_type = "Problema de acceso - Llaves/Puertas"
            severity = "Leve"
        elif "Daño menor" in label:
            damage_type = "Colisión - Daño menor"
            severity = "Leve"
        elif "Daño moderado" in label:
            damage_type = "Colisión - Daño moderado"
            severity = "Moderado"
        elif "Daño severo" in label:
            damage_type = "Colisión - Daño severo"
            severity = "Severo"
        elif "Pérdida total" in label:
            damage_type = "Colisión - Pérdida total"
            severity = "Crítico"
        elif "Sin daño" in label:
            damage_type = "Sin daño"
            severity = "Ninguno"
        
        print(f"Tipo de incidente: {damage_type}")
        print(f"Severidad: {severity}")
    else:
        print("No se obtuvieron resultados o el formato de respuesta no es el esperado.")
    
    print("\nProceso completado.")

if __name__ == "__main__":
    main() 