from flask import Flask, jsonify, request
from threading import Thread
import time

app = Flask(__name__)

# Function to dynamically add an endpoint
def dynamic_handler(name):
    def handler():
        return jsonify({
            'message': f"Dynamic route for {name} added at runtime!",
            'method': request.method
        })
    return handler

# Route to add new dynamic routes
@app.route('/add_route', methods=['POST'])
def add_route():
    route_data = request.json
    route_name = route_data.get('name')
    
    # Dynamically add the route while Flask is running
    app.add_url_rule(f"/dynamic/{route_name}", view_func=dynamic_handler(route_name), methods=['GET', 'POST'])
    
    return jsonify({
        'message': f"New route /dynamic/{route_name} added!",
        'success': True
    })

# Start the app
if __name__ == '__main__':
    app.run(debug=True)

