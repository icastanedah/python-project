import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import logging

# Intentar importar pillow-heif para manejar archivos HEIC
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False
    logging.warning("pillow-heif no está instalado. La conversión de archivos HEIC puede no funcionar correctamente.")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extensiones de archivo permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'heic', 'heif'}

def allowed_file(filename):
    """
    Verifica si el archivo tiene una extensión permitida
    
    Args:
        filename (str): Nombre del archivo
        
    Returns:
        bool: True si la extensión está permitida, False en caso contrario
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file, upload_folder):
    """
    Guarda una imagen subida por el usuario
    
    Args:
        file: Objeto de archivo de Flask
        upload_folder (str): Carpeta donde guardar la imagen
        
    Returns:
        str: Ruta al archivo guardado
    """
    try:
        # Generar un nombre de archivo seguro y único
        filename = secure_filename(file.filename)
        
        # Verificar si es un archivo HEIC/HEIF y convertirlo a JPEG
        if filename.lower().endswith(('.heic', '.heif')):
            # Cambiar la extensión a jpg para el nombre de archivo único
            base_name = os.path.splitext(filename)[0]
            unique_filename = f"{uuid.uuid4().hex}_{base_name}.jpg"
            temp_path = os.path.join(upload_folder, f"temp_{unique_filename}")
            file_path = os.path.join(upload_folder, unique_filename)
            
            # Guardar el archivo temporalmente
            file.save(temp_path)
            
            try:
                # Convertir HEIC a JPEG
                img = Image.open(temp_path)
                img.save(file_path, 'JPEG', quality=90)
                
                # Eliminar el archivo temporal
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                logger.info(f"Archivo HEIC convertido a JPEG: {file_path}")
            except Exception as e:
                logger.error(f"Error al convertir archivo HEIC: {str(e)}")
                # Si falla la conversión, intentamos usar el archivo original
                if os.path.exists(temp_path):
                    os.rename(temp_path, file_path)
        else:
            # Para otros formatos, proceder normalmente
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
        
        # Optimizar la imagen
        optimize_image(file_path)
        
        logger.info(f"Imagen guardada en: {file_path}")
        return file_path
    
    except Exception as e:
        logger.error(f"Error al guardar la imagen: {str(e)}")
        raise Exception(f"Error al guardar la imagen: {str(e)}")

def optimize_image(file_path, max_size=(1200, 1200)):
    """
    Optimiza una imagen redimensionándola si es necesario
    
    Args:
        file_path (str): Ruta al archivo de imagen
        max_size (tuple): Tamaño máximo (ancho, alto)
        
    Returns:
        None
    """
    try:
        # Abrir la imagen
        img = Image.open(file_path)
        
        # Verificar si la imagen necesita ser redimensionada
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Guardar la imagen optimizada
            img.save(file_path, optimize=True, quality=85)
            logger.info(f"Imagen optimizada: {file_path}")
    
    except Exception as e:
        logger.error(f"Error al optimizar la imagen: {str(e)}")
        # No lanzamos excepción para no interrumpir el flujo principal 