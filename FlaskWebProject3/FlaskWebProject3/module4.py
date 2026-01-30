# import sqlite3
# import os
# import json
# def add_file(tree, path):
#     current = tree
#     folders, filename = os.path.split(path)
#     for folder in folders.split(os.path.sep):
#         if folder not in current["children"]:
#             current["children"][folder] = {"type": "folder", "path": os.path.join(current["path"], folder), "children": {}}
#         current = current["children"][folder]
#     current["children"][filename] = {"type": "file", "path":  str(path).replace("{{DRIVE}}","||"), "children": {}}
#     #print(json.dumps(current, indent=4))

# def build_json_response(paths):
#     hierarchy = {"type": "", "path": "", "children": {}}
#     for path in paths:
#         add_file(hierarchy, str(path).replace("{{DRIVE}}",":"))
#     return hierarchy

# # Connect to the SQLite database
# conn = sqlite3.connect("D:\PyRepos\FlaskWebProject3\FlaskWebProject3\e67bd65687a3391c20bf93c3b587901b9c82050f4c86b465d0a5ec8f776d11e2.db")
# cursor = conn.cursor()

# # Execute the query to select file paths
# obj = "e67bd65687a3391c20bf93c3b587901b9c82050f4c86b465d0a5ec8f776d11e2"
# cursor.execute("SELECT replace(replace(full_file_name,'',''), '" + os.path.join(obj,"") + "','') FROM backups where name = " +"1715253960.2907739")

# # Fetch all file paths
# file_paths = [row[0] for row in cursor.fetchall()]

# # Close the cursor and connection
# cursor.close()
# conn.close()

# # Convert file paths into hierarchical JSON
# hierarchical_json = build_json_response(file_paths)

# # Print or use the hierarchical JSON
# import time
# with open(str(int(time.time()))+".json", "w") as f:
#     #print(json.dumps(hierarchical_json, indent=4))
#     json.dump(hierarchical_json, f, indent=4)

# # import sqlite3
# # import os
# # import json

# # # Connect to the SQLite database
# # conn = sqlite3.connect("D:\PyRepos\FlaskWebProject3\FlaskWebProject3\e67bd65687a3391c20bf93c3b587901b9c82050f4c86b465d0a5ec8f776d11e2.db")
# # cursor = conn.cursor()

# # # Execute the query to select file paths
# # cursor.execute("SELECT full_file_name FROM backups")

# # # Fetch all file paths
# # file_paths = [row[0] for row in cursor.fetchall()]

# # # Close the cursor and connection
# # cursor.close()
# # conn.close()

# # # Function to construct hierarchical JSON
# # def build_hierarchy(paths):
# #     hierarchy = {}

# #     for path in paths:
# #         print(path)
# #         current_node = hierarchy
# #         parts = path.split(os.path.sep)

# #         for part in parts:
# #             print(f"\t{part}")
# #             current_node = current_node.setdefault(part, {})

# #     return hierarchy

# # # Convert file paths into hierarchical JSON
# # hierarchical_json = json.dumps(build_hierarchy(file_paths), indent=8)

# # # Print or use the hierarchical JSON
# # print(hierarchical_json)

# #conn = sqlite3.connect("D:\PyRepos\FlaskWebProject3\FlaskWebProject3\e67bd65687a3391c20bf93c3b587901b9c82050f4c86b465d0a5ec8f776d11e2.db")