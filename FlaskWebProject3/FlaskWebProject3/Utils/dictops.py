# utils/json_operations.py
import json

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_record_by_id(dictionary, record_id):
    return dictionary.get(record_id)

def modify_record_by_id(dictionary, record_id, new_data):
    record = dictionary.get(record_id)
    if record:
        record.update(new_data)
        return True
    return False


# def get_record_by_id(dictionary, record_id):
#     return dictionary.get(record_id)

# def modify_record_by_id(dictionary, record_id, new_data):
#     record = dictionary.get(record_id)
#     if record:
#         record.update(new_data)
#         return True
#     return False

