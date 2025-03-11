from main import app

# Este archivo es el punto de entrada para Gunicorn
if __name__ == "__main__":
    app.run()

# Vercel busca una variable llamada 'app' para el despliegue
# Este archivo es necesario para que Vercel pueda encontrar la aplicación Flask 