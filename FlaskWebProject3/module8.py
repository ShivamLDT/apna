# import os
# import ctypes

# def list_files_in_shared_folder(share_path, username, password):
#     files = []
#     try:
         
#         # Create a connection to the shared folder with the provided credentials
#         net_use = ctypes.windll.winnetwk.WNetAddConnection2W
#         ctypes.WinDLL.win
#         net_use.restype = ctypes.c_uint
#         result = net_use(None, share_path, None, None, username, password, 0)
        
#         # Check if connection succeeded
#         if result == 0:
#             # List files in the shared folder
#             files = os.listdir(share_path)
#         else:
#             print("Failed to connect to shared folder. Error code:", result)
#     except FileNotFoundError:
#         print("Shared folder not found.")
#     except PermissionError:
#         print("Access denied to shared folder.")
#     return files

# # Usage
# share_path = "\\192.168.2.201"  # Replace computer_name and shared_folder with actual values
# username = 'user'
# password = 'Server@123'


 
# try:
#     win32wnet.WNetAddConnection2(win32netcon.RESOURCETYPE_DISK, 'Z:','\\\\192.168.2.201', None, username,password, 0)
#     print ("connection established successfully")
# except Exception as dw:
#     print  ("connection not established" )
#     print  (str(dw) )
# files = list_files_in_shared_folder(share_path, username, password)
# if files:
#     print("Files available in the shared folder:")
#     for file in files:
#         print(file)
