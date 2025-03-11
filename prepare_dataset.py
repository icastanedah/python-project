#!/usr/bin/env python3
"""
Script para preparar un conjunto de datos de imágenes para Vertex AI AutoML Vision.
Este script:
1. Crea un bucket en Google Cloud Storage (si no existe)
2. Sube imágenes desde carpetas locales al bucket
3. Genera un archivo CSV con las rutas de las imágenes y sus etiquetas
"""

import os
import argparse
import csv
from google.cloud import storage
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Categorías de daños en vehículos
DAMAGE_CATEGORIES = [
    "Fallo mecánico - Batería",
    "Fallo mecánico - Llanta pinchada",
    "Fallo mecánico - Fuga de líquido",
    "Problema de acceso - Llaves/Puertas",
    "Colisión - Daño menor",
    "Colisión - Daño moderado",
    "Colisión - Daño severo",
    "Colisión - Pérdida total",
    "Sin daño"
]

def create_bucket_if_not_exists(bucket_name, project_id, location="us-central1"):
    """Crea un bucket en Google Cloud Storage si no existe."""
    storage_client = storage.Client(project=project_id)
    
    # Verificar si el bucket ya existe
    if storage_client.lookup_bucket(bucket_name):
        print(f"El bucket {bucket_name} ya existe.")
        return
    
    # Crear el bucket
    bucket = storage_client.create_bucket(bucket_name, location=location)
    print(f"Bucket {bucket.name} creado en {location}.")

def upload_images_to_gcs(local_dir, bucket_name, gcs_path, project_id):
    """Sube imágenes desde un directorio local a Google Cloud Storage."""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    
    # Lista para almacenar las rutas de las imágenes y sus etiquetas
    image_paths = []
    
    # Recorrer las carpetas de categorías
    for category_folder in os.listdir(local_dir):
        category_path = os.path.join(local_dir, category_folder)
        
        # Verificar que sea un directorio
        if not os.path.isdir(category_path):
            continue
        
        # Mapear el nombre de la carpeta a la categoría
        category_label = map_folder_to_category(category_folder)
        if not category_label:
            print(f"Advertencia: La carpeta {category_folder} no corresponde a una categoría conocida. Se omitirá.")
            continue
        
        print(f"Procesando categoría: {category_label}")
        
        # Recorrer las imágenes en la carpeta
        for image_file in os.listdir(category_path):
            # Verificar que sea una imagen
            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                continue
            
            # Ruta local de la imagen
            local_image_path = os.path.join(category_path, image_file)
            
            # Ruta en GCS
            gcs_image_path = f"{gcs_path}/{category_folder}/{image_file}"
            
            # Subir la imagen
            blob = bucket.blob(gcs_image_path)
            blob.upload_from_filename(local_image_path)
            
            # Añadir a la lista
            image_paths.append((f"gs://{bucket_name}/{gcs_image_path}", category_label))
            
            print(f"  Subida: {image_file}")
    
    return image_paths

def map_folder_to_category(folder_name):
    """Mapea el nombre de la carpeta a una categoría de daño."""
    folder_name = folder_name.lower()
    
    # Mapeo de nombres de carpetas a categorías
    mapping = {
        "bateria": "Fallo mecánico - Batería",
        "battery": "Fallo mecánico - Batería",
        "llanta": "Fallo mecánico - Llanta pinchada",
        "tire": "Fallo mecánico - Llanta pinchada",
        "flat_tire": "Fallo mecánico - Llanta pinchada",
        "fuga": "Fallo mecánico - Fuga de líquido",
        "leak": "Fallo mecánico - Fuga de líquido",
        "fluid": "Fallo mecánico - Fuga de líquido",
        "acceso": "Problema de acceso - Llaves/Puertas",
        "access": "Problema de acceso - Llaves/Puertas",
        "keys": "Problema de acceso - Llaves/Puertas",
        "door": "Problema de acceso - Llaves/Puertas",
        "menor": "Colisión - Daño menor",
        "minor": "Colisión - Daño menor",
        "moderado": "Colisión - Daño moderado",
        "moderate": "Colisión - Daño moderado",
        "severo": "Colisión - Daño severo",
        "severe": "Colisión - Daño severo",
        "total": "Colisión - Pérdida total",
        "total_loss": "Colisión - Pérdida total",
        "sin_dano": "Sin daño",
        "no_damage": "Sin daño",
        "normal": "Sin daño"
    }
    
    # Buscar coincidencias parciales
    for key, value in mapping.items():
        if key in folder_name:
            return value
    
    return None

def create_csv_file(image_paths, output_file):
    """Crea un archivo CSV con las rutas de las imágenes y sus etiquetas."""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Escribir encabezado
        writer.writerow(['GCS_FILE_PATH', 'LABEL'])
        # Escribir datos
        for path, label in image_paths:
            writer.writerow([path, label])
    
    print(f"Archivo CSV creado: {output_file}")

def upload_csv_to_gcs(csv_file, bucket_name, gcs_path, project_id):
    """Sube el archivo CSV a Google Cloud Storage."""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    
    # Ruta en GCS
    gcs_csv_path = f"{gcs_path}/{os.path.basename(csv_file)}"
    
    # Subir el archivo
    blob = bucket.blob(gcs_csv_path)
    blob.upload_from_filename(csv_file)
    
    print(f"Archivo CSV subido a: gs://{bucket_name}/{gcs_csv_path}")
    return f"gs://{bucket_name}/{gcs_csv_path}"

def main():
    parser = argparse.ArgumentParser(description='Preparar conjunto de datos para Vertex AI AutoML Vision')
    parser.add_argument('--local_dir', required=True, help='Directorio local con las imágenes organizadas en carpetas por categoría')
    parser.add_argument('--bucket_name', required=True, help='Nombre del bucket de Google Cloud Storage')
    parser.add_argument('--gcs_path', default='vehicle_damage_dataset', help='Ruta dentro del bucket para las imágenes')
    parser.add_argument('--csv_file', default='vehicle_damage_dataset.csv', help='Nombre del archivo CSV a generar')
    
    args = parser.parse_args()
    
    # Obtener el ID del proyecto desde las variables de entorno
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        raise ValueError("La variable de entorno GOOGLE_CLOUD_PROJECT no está configurada")
    
    # Crear el bucket si no existe
    create_bucket_if_not_exists(args.bucket_name, project_id)
    
    # Subir las imágenes
    image_paths = upload_images_to_gcs(args.local_dir, args.bucket_name, args.gcs_path, project_id)
    
    # Crear el archivo CSV
    create_csv_file(image_paths, args.csv_file)
    
    # Subir el archivo CSV
    gcs_csv_path = upload_csv_to_gcs(args.csv_file, args.bucket_name, args.gcs_path, project_id)
    
    print("\nProceso completado.")
    print(f"Total de imágenes procesadas: {len(image_paths)}")
    print(f"Archivo CSV en GCS: {gcs_csv_path}")
    print("\nPuedes usar esta ruta para crear un conjunto de datos en Vertex AI.")

if __name__ == "__main__":
    main() 