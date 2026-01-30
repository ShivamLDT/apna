

import os

def get_directory_contents(path):
    try:
        contents = os.listdir(path)
        return contents
    except Exception as e:
        return str(e)

def get_file_content(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        return content
    except Exception as e:
        return str(e)

def get_parent_directory(path):
    return os.path.abspath(os.path.join(path, os.pardir))
