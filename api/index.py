import sys
import os

# Añadir el directorio raíz al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la aplicación Flask desde app/app.py
from app.app import app

# Vercel busca una variable llamada 'app' para el despliegue
# No es necesario ejecutar app.run() aquí, Vercel lo hará automáticamente 