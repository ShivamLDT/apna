import os
import re
import shutil
from flask import Flask

# Directory to save Blueprints
BLUEPRINTS_DIR = 'blueprints'
# List to store routes for updating in the main application file
all_routes = []

def create_blueprint_files(app):
    if not os.path.exists(BLUEPRINTS_DIR):
        os.makedirs(BLUEPRINTS_DIR)

    for rule in app.url_map.iter_rules():
        endpoint = app.view_functions[rule.endpoint]
        route = str(rule)
        func_name = endpoint.__name__
        module = endpoint.__module__

        blueprint_name = route.strip('/').split('/')[0]
        blueprint_file = os.path.join(BLUEPRINTS_DIR, f'{blueprint_name}.py')

        if not os.path.exists(blueprint_file):
            with open(blueprint_file, 'w') as f:
                f.write(f'from flask import Blueprint, jsonify\n\n')
                f.write(f'{blueprint_name}_bp = Blueprint(\'{blueprint_name}\', __name__)\n\n')

        with open(module.replace('.', '/') + '.py', 'r') as f:
            content = f.read()

        route_pattern = re.compile(rf'def {func_name}\(.*?\n(.*?)\n\n', re.DOTALL)
        route_code = route_pattern.search(content).group(1).strip()

        with open(blueprint_file, 'a') as f:
            f.write(f'@{blueprint_name}_bp.route(\'{route}\')\n')
            f.write(f'def {func_name}():\n')
            for line in route_code.split('\n'):
                f.write(f'    {line}\n')
            f.write('\n')

        all_routes.append((route, func_name, blueprint_name))


def update_file(module, func_name, route):
    file_path = module.replace('.', '/') + '.py'
    with open(file_path, 'r') as f:
        content = f.read()

    route_pattern = re.compile(rf'@app\.route\([\'"]{route}[\'"]\)\ndef {func_name}\(.*?\n(.*?)\n\n', re.DOTALL)
    content = route_pattern.sub('', content)

    with open(file_path, 'w') as f:
        f.write(content)


def update_main_app_file(app_file, all_routes):
    with open(app_file, 'r') as f:
        content = f.read()

    blueprint_imports = []
    blueprint_registrations = []
    for route, _, blueprint_name in all_routes:
        blueprint_import = f'from blueprints.{blueprint_name} import {blueprint_name}_bp'
        if blueprint_import not in blueprint_imports:
            blueprint_imports.append(blueprint_import)
        blueprint_registrations.append(f'app.register_blueprint({blueprint_name}_bp)')

    imports_code = '\n'.join(blueprint_imports)
    registrations_code = '\n'.join(blueprint_registrations)

    content = re.sub(r'(from flask import Flask.*?\n)', rf'\1{imports_code}\n', content, flags=re.DOTALL)
    content = re.sub(r'(app = Flask\(__name__\).*?\n)', rf'\1{registrations_code}\n', content, flags=re.DOTALL)

    with open(app_file, 'w') as f:
        f.write(content)


def refactor_project(app, directory):
    create_blueprint_files(app)

    for rule in app.url_map.iter_rules():
        endpoint = app.view_functions[rule.endpoint]
        route = str(rule)
        func_name = endpoint.__name__
        module = endpoint.__module__
        update_file(module, func_name, route)

    for root, _, files in os.walk(directory):
        for file in files:
            if 'app' in file.lower() and file.endswith('.py'):
                app_file = os.path.join(root, file)
                update_main_app_file(app_file, all_routes)


def main():
    # Create a temporary Flask app to load routes
    app = Flask(__name__)

    # Import all modules to ensure routes are registered
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                module_path = os.path.join(root, file).replace('/', '.').replace('\\', '.').rstrip('.py')
                __import__(module_path)

    refactor_project(app, os.getcwd())
    print('Refactoring complete!')


if __name__ == '__main__':
    main()
