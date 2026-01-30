# from flask import request, jsonify
# import os
# import threading
# import time
# import gzip
# import base64
# import datetime
# import pytz
# import requests
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from FlaskWebProject3 import views
# from module2 import BackupLogs, BackupMain
# from sqlite_manager import SQLiteManager  # Assume this is a custom module

# class BackupService:
#     def __init__(self, app):
#         self.app = app
#         self.sqlite_manager = SQLiteManager()
#         self.date_format = "%d/%m/%Y, %I:%M:%S %p"
#         self.timezone = pytz.timezone("Asia/Kolkata")
#         self.db_key = ""
#     def get_restore_data(self):
#         try:
#             request_data = request.json
#         except Exception as e:
#             return jsonify(result={"reason": "Invalid JSON request"}), 400

#         action = request_data.get("action", "fetch").lower()
#         storage_type = request_data.get("storageType", "LAN").lower().replace(" ", "")
#         storage_type_json = request_data.get("deststorageType", {"typ": "LAN"})
#         agent_name = request_data.get("agentName", "DESKTOP-SUCRQP8")
#         start_date = request_data.get("startDate", "01/01/2024, 00:00:00 am")
#         end_date = request_data.get("endDate", "31/12/2030, 23:59:59 pm")
#         extensions = request_data.get("selectedExtensions", ["*.*"])

#         storage_type = self._map_storage_type(storage_type)
#         storage_type_details = self._get_storage_type_details(storage_type_json)
#         agent = self._search_client_nodes(agent_name).get("agent")
#         obj = self._search_client_nodes(agent)
#         obj_ip = obj.get("ipAddress")
#         db_key = views.clientnodes_x[obj_ip].get("key")

#         if action == "restore":
#             return self._handle_restore(request_data, db_key, obj_ip, storage_type)
#         elif action == "browse":
#             return self._handle_browse(request_data, db_key, storage_type)
#         elif action == "fetch":
#             return self._handle_fetch(request_data, db_key, agent, storage_type, start_date, end_date)
#         else:
#             return jsonify(result={"reason": "Invalid action"}), 400

#     def _map_storage_type(self, storage_type):
#         storage_type_mapping = {
#             "gdrive": "GDRIVE",
#             "googledrive": "GDRIVE",
#         }
#         return storage_type_mapping.get(storage_type, storage_type.upper())

#     def _get_storage_type_details(self, storage_type_json):
#         return {
#             "typ": storage_type_json.get("typ", "LAN"),
#             "ipc": storage_type_json.get("ipc", ""),
#             "uid": storage_type_json.get("uid", ""),
#             "idn": storage_type_json.get("idn", ""),
#             "loc": storage_type_json.get("loc", ""),
#         }

#     def _search_client_nodes(self, agent_name):
#         # Placeholder for the actual search function
#         return {}

#     def _handle_restore(self, request_data, db_key, obj_ip, storage_type):
#         try:
#             selected_id = request_data.get("id", "0")
#             target_location = request_data.get("targetLocation", "")
#             source_location = request_data.get("sourceLocation", "")
#             selected_files = request_data.get("selectedFiles", [])
#             restore_location = request_data.get("RestoreLocation", target_location) or target_location

#             if selected_files:
#                 files_str = self._build_files_str(selected_files, db_key)
#                 file_paths = self._fetch_file_paths(db_key, selected_id, storage_type, files_str)
#                 restore_headers = self._build_restore_headers(file_paths, target_location, restore_location, storage_type,db_key)
#                 responses = self._send_restore_requests(restore_headers, obj_ip)

#                 return jsonify(result=responses), 200

#             return jsonify(result={"reason": "No files selected for restore"}), 400
#         except Exception as e:
#             return jsonify(result={"reason": str(e)}), 500

#     def _handle_browse(self, request_data, db_key, storage_type):
#         try:
#             selected_id = request_data.get("id", "0")
#             all_types, selected_types = self._get_extension_types(request_data.get("selectedExtensions", ["*.*"]))
#             query = self._build_browse_query(db_key, selected_id, storage_type, all_types, selected_types)
#             file_paths = self._execute_query(db_key, query)
#             response_data = self._build_json_response(file_paths)

#             return jsonify(response_data), 200
#         except Exception as e:
#             return jsonify(result={"reason": str(e)}), 500

#     def _handle_fetch(self, request_data, db_key, agent, storage_type, start_date, end_date):
#         try:
#             start_timestamp = self._convert_to_timestamp(start_date)
#             end_timestamp = self._convert_to_timestamp(end_date)
#             query = self._build_fetch_query(db_key, agent, storage_type, start_timestamp, end_timestamp)
#             backup_jobs = self._execute_fetch_query(db_key, query)

#             return jsonify(backup_jobs), 200
#         except Exception as e:
#             return jsonify(result={"reason": str(e)}), 500

#     def _convert_to_timestamp(self, date_str):
#         date = datetime.datetime.strptime(date_str, self.date_format)
#         localized_date = self.timezone.localize(date)
#         return int(localized_date.timestamp() * 1000)

#     def _build_files_str(self, selected_files, db_key):
#         return ",".join(
#             f"'{os.path.join(db_key, file.replace(':', '{{DRIVE}}'))}'" for file in selected_files
#         )

#     def _fetch_file_paths(self, db_key, selected_id, storage_type, files_str):
#         dbname = os.path.join(self.app.config["location"], db_key) + ".db"
#         query = f"SELECT * FROM backups WHERE name = {selected_id} AND data_repo = '{storage_type}' AND full_file_name IN ({files_str})"
#         results = self.sqlite_manager.execute_queries([(dbname, [query])])
#         return [record for db_path, db_results in results.items() for result, records in db_results if result == "Success" for record in records]

#     def _build_restore_headers(self, file_paths, target_location, restore_location, storage_type,db_key):
#         headers = []
#         for rec in file_paths:
#             header = {
#                 "id": str(rec[0]),
#                 "pid": str(rec[1]),
#                 "obj": str(db_key),
#                 "tcc": self._compress_and_encode(str(rec[9])),
#                 "rep": self._compress_and_encode(storage_type),
#                 "repd": self._compress_and_encode(str(rec[10])),
#                 "tccn": self._compress_and_encode(os.path.join(str(rec[4]).replace(target_location.replace(":", "{{DRIVE}}"), restore_location.replace(":", "{{DRIVE}}")), str(rec[8])))
#             }
#             headers.append(header)
#         return headers

#     def _send_restore_requests(self, headers, obj_ip):
#         responses = []
#         for header in headers:
#             try:
#                 res = requests.post(f"{obj_ip}/restoretest", headers=header, json={"test": "0"})
#                 responses.append(res.json())
#             except Exception as e:
#                 responses.append({"error": str(e)})
#         return responses

#     def _compress_and_encode(self, data):
#         return base64.b64encode(gzip.compress(data.encode("UTF-8"), 9, mtime=time.time())).decode("utf-8")

#     def _get_extension_types(self, extensions):
#         all_types = "*.*" in extensions
#         selected_types = {ext for ext in extensions if ext != "*.*"}
#         return all_types, selected_types

#     def _build_browse_query(self, db_key, selected_id, storage_type, all_types, selected_types):
#         base_query = f"SELECT replace(replace(full_file_name,'',''), '{os.path.join(db_key, '')}', '') FROM backups WHERE name = {selected_id} AND data_repo = '{storage_type}'"
#         if not all_types and selected_types:
#             filter_query = " AND (" + " OR ".join([f"full_file_name LIKE '%{ext}'" for ext in selected_types]) + ")"
#             return base_query + filter_query
#         return base_query

#     def _execute_query(self, db_key, query):
#         dbname = os.path.join(self.app.config["location"], db_key) + ".db"
#         results = self.sqlite_manager.execute_queries([(dbname, [query])])
#         return [file[0] for db_path, db_results in results.items() for result, records in db_results if result == "Success" for file in records]

#     def _build_json_response(self, file_paths):
#         # Implement the function to build a JSON response based on the file paths
#         return {}

#     def _build_fetch_query(self, db_key, agent, storage_type, start_timestamp, end_timestamp):
#         return (
#             f"SELECT backups_M.id, date_time, from_computer, from_path, data_repo, mime_type, file_name, size, pNameText, pIdText, bkupType "
#             f"FROM backups_M WHERE ((id * 1000 >= {start_timestamp}) AND (id * 1000 <= {end_timestamp})) AND "
#             f"from_computer = '{agent}' AND data_repo = '{storage_type}'"
#         )

#     def _execute_fetch_query(self, db_key, query):
#         dbname = os.path.join(self.app.config["location"], db_key) + ".db"
#         results = self.sqlite_manager.execute_queries([(dbname, [query])])
#         return [
#             {"id": str(rec[0]), "dateTime": str(rec[1]), "fromComputer": str(rec[2]), "fromPath": str(rec[3]), "dataRepo": str(rec[4]), "mimeType": str(rec[5]), "fileName": str(rec[6]), "size": str(rec[7]), "pNameText": str(rec[8]), "pIdText": str(rec[9]), "bkupType": str(rec[10])}
#             for db_path, db_results in results.items()
#             for result, records in db_results if result == "Success"
#             for rec in records
#         ]
