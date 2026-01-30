# import os
# import pkgutil
# import importlib
# import inspect
# from flask import Flask

# class FlaskBlueprintRefactor:
#     def __init__(self, package_name):
#         self.package_name = package_name
#         self.modules = self.import_submodules(package_name)
#         self.apps = self.find_flask_apps(self.modules)
    
#     def is_flask_app(self, obj):
#         return isinstance(obj, Flask)

#     def import_submodules(self, package_name):
#         modules = []
#         package = importlib.import_module(package_name)
#         for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
#             try:
#                 module = importlib.import_module(name)
#                 modules.append(module)
#             except ImportError as e:
#                 print(f"Failed to import {name}: {e}")
#         return modules

#     def find_flask_apps(self, modules):
#         apps = []
#         for module in modules:
#             for name, obj in inspect.getmembers(module):
#                 if self.is_flask_app(obj):
#                     apps.append(obj)
#         return apps

#     def list_routes(self, app):
#         routes = []
#         for rule in app.url_map.iter_rules():
#             route_info = {
#                 "endpoint": rule.endpoint,
#                 "methods": rule.methods,
#                 "rule": rule.rule,
#             }
#             routes.append(route_info)
#         return routes

#     def create_blueprint_code(self, app_name, route):
#         blueprint_code = f"""
# from flask import Blueprint, current_app

# {route['endpoint']} = Blueprint('{route["endpoint"]}', __name__)

# @{route['endpoint']}.route('/api/v2/_xx_{route["rule"]}', methods={list(route["methods"])})
# def {route["endpoint"]}():
#     return current_app.view_functions['{route["endpoint"]}']()
# """
#         return blueprint_code

#     def save_blueprint(self, app_name, route, blueprint_code):
#         dir_path = os.path.join('blueprints', app_name)
#         os.makedirs(dir_path, exist_ok=True)
#         file_path = os.path.join(dir_path, f'{route["endpoint"]}.py')
#         with open(file_path, 'w') as f:
#             f.write(blueprint_code)

#     def generate_blueprints(self):
#         for app in self.apps:
#             app_name = app.import_name.split('.')[-1]
#             routes = self.list_routes(app)
#             for route in routes:
#                 blueprint_code = self.create_blueprint_code(app_name, route)
#                 self.save_blueprint(app_name, route, blueprint_code)

#     def register_blueprints(self, app):
#         for root, _, files in os.walk('blueprints'):
#             for file in files:
#                 if file.endswith('.py'):
#                     module_path = os.path.join(root, file).replace(os.path.sep, '.').rstrip('.py')
#                     blueprint_module = importlib.import_module(module_path)
#                     if hasattr(blueprint_module, 'bp'):
#                         app.register_blueprint(blueprint_module.bp)

# # Example usage
# if __name__ == '__main__':
#     # Define the main package name
#     package_name = 'FlaskWebProject3'
    
#     # Initialize the refactor class
#     refactor = FlaskBlueprintRefactor(package_name)
    
#     # Generate blueprints
#     refactor.generate_blueprints()
    
#     # Assuming your main Flask app is in app.py
#     from FlaskWebProject3 import app
    
#     # Register the generated blueprints
#     refactor.register_blueprints(app)
    
#     # Run the app for testing
#     app.run(debug=True)

