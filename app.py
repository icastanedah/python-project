from main import app

# Este archivo es necesario para que Gunicorn pueda encontrar la aplicación Flask
# cuando se ejecuta con 'gunicorn app:app'

# La variable 'app' ya está importada desde main.py y está disponible para Gunicorn 