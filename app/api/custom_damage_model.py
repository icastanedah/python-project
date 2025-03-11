import os
import logging
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_vertex_ai():
    """Inicializa Vertex AI con las credenciales adecuadas"""
    try:
        aiplatform.init(
            project=os.environ.get('GOOGLE_CLOUD_PROJECT'),
            location=os.environ.get('GOOGLE_CLOUD_REGION', 'us-central1')
        )
        logger.info(f"Vertex AI inicializado para el proyecto: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    except Exception as e:
        logger.error(f"Error al inicializar Vertex AI: {str(e)}")
        raise

def predict_damage(image_path, threshold=0.5):
    """
    Predice el tipo de daño en una imagen usando el modelo personalizado de Vertex AI
    
    Args:
        image_path (str): Ruta al archivo de imagen
        threshold (float): Umbral de confianza mínimo para considerar una predicción
        
    Returns:
        dict: Resultados de la predicción
    """
    try:
        # ID del modelo y endpoint (estos valores se obtienen después de entrenar el modelo)
        model_id = os.environ.get('VERTEX_MODEL_ID')
        endpoint_id = os.environ.get('VERTEX_ENDPOINT_ID')
        
        if not model_id or not endpoint_id:
            logger.error("VERTEX_MODEL_ID o VERTEX_ENDPOINT_ID no configurados en variables de entorno")
            return {
                'error': "Modelo personalizado no configurado correctamente",
                'incident_type': 'Error',
                'damage_severity': 'Error',
                'vehicle_type': 'Error',
                'damaged_parts': [],
                'confidence': 0.0
            }
        
        # Inicializar Vertex AI
        init_vertex_ai()
        
        # Cargar la imagen
        with open(image_path, "rb") as f:
            image_content = f.read()
        
        # Codificar la imagen en base64
        import base64
        encoded_content = base64.b64encode(image_content).decode("utf-8")
        
        # Crear la instancia para la predicción
        instance = predict.instance.ImageClassificationPredictionInstance(
            content=encoded_content,
        ).to_value()
        
        # Obtener el endpoint
        endpoint = aiplatform.Endpoint(endpoint_id)
        
        # Realizar la predicción
        logger.info(f"Enviando imagen a Vertex AI para predicción: {image_path}")
        prediction = endpoint.predict([instance])
        
        # Procesar los resultados
        results = []
        
        # El formato exacto de la respuesta puede variar según cómo se entrenó el modelo
        # Ajusta esta parte según sea necesario después de entrenar el modelo
        if hasattr(prediction.predictions[0], 'displayNames') and hasattr(prediction.predictions[0], 'confidences'):
            for label, score in zip(prediction.predictions[0]['displayNames'], 
                                prediction.predictions[0]['confidences']):
                if score >= threshold:
                    results.append({
                        'label': label,
                        'confidence': round(score * 100, 2)
                    })
        else:
            # Formato alternativo de respuesta
            logger.info(f"Formato de respuesta alternativo: {prediction.predictions}")
            for pred in prediction.predictions:
                if isinstance(pred, dict) and 'label' in pred and 'score' in pred:
                    if pred['score'] >= threshold:
                        results.append({
                            'label': pred['label'],
                            'confidence': round(pred['score'] * 100, 2)
                        })
        
        # Ordenar por confianza
        results = sorted(results, key=lambda x: x['confidence'], reverse=True)
        
        # Determinar el tipo de incidente y la severidad basado en la predicción principal
        incident_type = "Desconocido"
        damage_severity = "Desconocido"
        damaged_parts = []
        
        if results:
            top_prediction = results[0]['label']
            
            # Mapear la predicción a los tipos de incidentes de tu aplicación
            if "Batería" in top_prediction:
                incident_type = "Fallo mecánico - Batería"
                damage_severity = "Moderado"
                damaged_parts = ["Batería", "Sistema eléctrico"]
            elif "Llanta" in top_prediction:
                incident_type = "Fallo mecánico - Llanta pinchada"
                damage_severity = "Moderado"
                damaged_parts = ["Llanta", "Neumático"]
            elif "Fuga" in top_prediction or "Líquido" in top_prediction:
                incident_type = "Fallo mecánico - Fuga de líquido"
                damage_severity = "Moderado"
                damaged_parts = ["Motor", "Sistema de fluidos"]
            elif "Acceso" in top_prediction:
                incident_type = "Problema de acceso - Llaves/Puertas"
                damage_severity = "Leve"
                damaged_parts = ["Cerradura", "Puerta"]
            elif "Daño menor" in top_prediction:
                incident_type = "Colisión - Daño menor"
                damage_severity = "Leve"
                damaged_parts = ["Carrocería"]
            elif "Daño moderado" in top_prediction:
                incident_type = "Colisión - Daño moderado"
                damage_severity = "Moderado"
                damaged_parts = ["Carrocería", "Parachoques"]
            elif "Daño severo" in top_prediction:
                incident_type = "Colisión - Daño severo"
                damage_severity = "Severo"
                damaged_parts = ["Carrocería", "Parachoques", "Estructura"]
            elif "Pérdida total" in top_prediction:
                incident_type = "Colisión - Pérdida total"
                damage_severity = "Crítico"
                damaged_parts = ["Carrocería", "Estructura", "Motor"]
            elif "Sin daño" in top_prediction:
                incident_type = "Sin daño"
                damage_severity = "Ninguno"
                damaged_parts = []
        
        logger.info(f"Predicción completada. Tipo de incidente: {incident_type}, Severidad: {damage_severity}")
        
        return {
            'incident_type': incident_type,
            'damage_severity': damage_severity,
            'vehicle_type': 'Automóvil',  # Esto podría refinarse con más análisis
            'damaged_parts': damaged_parts,
            'confidence': results[0]['confidence'] if results else 0.0,
            'predictions': results
        }
    
    except Exception as e:
        logger.error(f"Error al predecir daño con modelo personalizado: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            'error': f"Error al predecir daño con modelo personalizado: {str(e)}",
            'incident_type': 'Error',
            'damage_severity': 'Error',
            'vehicle_type': 'Error',
            'damaged_parts': [],
            'confidence': 0.0
        } 