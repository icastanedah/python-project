#!/usr/bin/env python3
"""
Script para probar el envío de datos a una API externa.
Este script simula una API externa que recibe datos de la aplicación.
"""

import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/receive-data', methods=['POST'])
def receive_data():
    """
    Endpoint para recibir datos de la aplicación principal.
    """
    try:
        # Verificar si se enviaron datos JSON
        if not request.is_json:
            return jsonify({'error': 'No se enviaron datos JSON'}), 400
        
        # Obtener los datos
        data = request.json
        
        # Imprimir los datos recibidos
        print("Datos recibidos:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Guardar los datos en un archivo
        with open('received_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Responder con éxito
        return jsonify({
            'success': True,
            'message': 'Datos recibidos correctamente',
            'timestamp': data.get('timestamp', '')
        })
    
    except Exception as e:
        print(f"Error al procesar los datos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error al procesar los datos: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("Iniciando servidor de prueba en http://localhost:3000")
    print("Endpoint disponible en: http://localhost:3000/api/receive-data")
    app.run(host='0.0.0.0', port=3000, debug=True) 