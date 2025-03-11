#!/usr/bin/env python3
"""
Script para entrenar un modelo de clasificación de imágenes en Vertex AI.
Este script:
1. Crea un conjunto de datos en Vertex AI
2. Inicia un trabajo de entrenamiento de AutoML Vision
3. Despliega el modelo entrenado en un endpoint
"""

import os
import argparse
import time
from google.cloud import aiplatform
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_dataset(project_id, location, display_name, gcs_csv_path):
    """Crea un conjunto de datos de imágenes en Vertex AI."""
    # Inicializar Vertex AI
    aiplatform.init(project=project_id, location=location)
    
    # Crear el conjunto de datos
    dataset = aiplatform.ImageDataset.create(
        display_name=display_name,
        gcs_source=[gcs_csv_path],
        import_schema_uri=aiplatform.schema.dataset.ioformat.image.single_label_classification,
        sync=True
    )
    
    print(f"Conjunto de datos creado: {dataset.resource_name}")
    return dataset

def train_automl_model(dataset, model_display_name, training_budget_hours=8):
    """Entrena un modelo AutoML Vision."""
    # Convertir horas a milisegundos
    budget_milli_node_hours = training_budget_hours * 1000
    
    # Iniciar el entrenamiento
    model = aiplatform.AutoMLImageTrainingJob(
        display_name=model_display_name,
        prediction_type="classification",
        multi_label=False,
        model_type="CLOUD",
        base_model=None
    ).run(
        dataset=dataset,
        model_display_name=model_display_name,
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        budget_milli_node_hours=budget_milli_node_hours,
        disable_early_stopping=False
    )
    
    print(f"Modelo entrenado: {model.resource_name}")
    return model

def deploy_model(model, machine_type="n1-standard-2"):
    """Despliega el modelo en un endpoint."""
    # Crear un endpoint
    endpoint = aiplatform.Endpoint.create(
        display_name=f"{model.display_name}-endpoint"
    )
    
    # Desplegar el modelo
    model.deploy(
        endpoint=endpoint,
        machine_type=machine_type,
        min_replica_count=1,
        max_replica_count=1
    )
    
    print(f"Modelo desplegado en el endpoint: {endpoint.resource_name}")
    print(f"ID del modelo: {model.name}")
    print(f"ID del endpoint: {endpoint.name}")
    
    # Guardar los IDs en un archivo para referencia futura
    with open("model_info.txt", "w") as f:
        f.write(f"MODEL_ID={model.name}\n")
        f.write(f"ENDPOINT_ID={endpoint.name}\n")
    
    return endpoint

def main():
    parser = argparse.ArgumentParser(description='Entrenar un modelo de clasificación de imágenes en Vertex AI')
    parser.add_argument('--gcs_csv_path', required=True, help='Ruta al archivo CSV en GCS con las imágenes y etiquetas')
    parser.add_argument('--dataset_name', default='vehicle_damage_dataset', help='Nombre para el conjunto de datos')
    parser.add_argument('--model_name', default='vehicle_damage_model', help='Nombre para el modelo')
    parser.add_argument('--training_hours', type=int, default=8, help='Presupuesto de entrenamiento en horas')
    parser.add_argument('--deploy', action='store_true', help='Desplegar el modelo después del entrenamiento')
    parser.add_argument('--machine_type', default='n1-standard-2', help='Tipo de máquina para el despliegue')
    
    args = parser.parse_args()
    
    # Obtener el ID del proyecto y la ubicación desde las variables de entorno
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('GOOGLE_CLOUD_REGION', 'us-central1')
    
    if not project_id:
        raise ValueError("La variable de entorno GOOGLE_CLOUD_PROJECT no está configurada")
    
    # Crear el conjunto de datos
    print(f"Creando conjunto de datos: {args.dataset_name}")
    dataset = create_dataset(project_id, location, args.dataset_name, args.gcs_csv_path)
    
    # Entrenar el modelo
    print(f"Iniciando entrenamiento del modelo: {args.model_name}")
    print(f"Presupuesto de entrenamiento: {args.training_hours} horas")
    model = train_automl_model(dataset, args.model_name, args.training_hours)
    
    # Desplegar el modelo si se solicita
    if args.deploy:
        print(f"Desplegando modelo en un endpoint con máquina tipo: {args.machine_type}")
        endpoint = deploy_model(model, args.machine_type)
        
        # Actualizar el archivo .env con los IDs del modelo y endpoint
        with open(".env", "a") as f:
            f.write(f"\n# IDs del modelo y endpoint generados el {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"VERTEX_MODEL_ID={model.name}\n")
            f.write(f"VERTEX_ENDPOINT_ID={endpoint.name}\n")
        
        print("\nLos IDs del modelo y endpoint se han añadido al archivo .env")
    else:
        print("\nEl modelo ha sido entrenado pero no desplegado.")
        print("Para desplegarlo más tarde, ejecuta este script con la opción --deploy")
    
    print("\nProceso completado.")

if __name__ == "__main__":
    main() 