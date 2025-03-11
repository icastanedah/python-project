from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    """
    Endpoint para recibir datos de la aplicación principal
    """
    try:
        # Obtener los datos JSON enviados
        data = request.json
        
        # Guardar los datos en un archivo para referencia
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"received_data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Datos recibidos y guardados en {filename}")
        print("Estructura de datos recibida:")
        print(json.dumps(data, indent=2))
        
        # Devolver una respuesta exitosa
        return jsonify({
            "success": True,
            "message": f"Datos recibidos correctamente y guardados en {filename}",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error al procesar los datos: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == "__main__":
    print("Iniciando servidor de prueba en http://localhost:5001/receive_data")
    print("Este servidor recibirá los datos enviados desde la aplicación principal")
    print("Para detener el servidor, presiona Ctrl+C")
    app.run(host='0.0.0.0', port=5001, debug=True) 