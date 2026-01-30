# from smbprotocol.connection import Connection
# from smbprotocol.session import Session
# from smbprotocol.tree import TreeConnect
# from smbprotocol.open import Open
# from smbprotocol.file_info import FileInformationClass
# from smbprotocol.file_info import FileAttributes 
# import uuid
# import os

# # Establish connection
# server_ip = "192.168.2.201"
# username = "user"
# password = "Server@123"
# share_name = "Backups"


# try:
#     # Create a new connection
#     connection = Connection(uuid.uuid4(), server_ip)
#     connection.connect()
    
#     # Perform session setup
#     session = Session(connection, username, password)
#     session.connect()
    
#     # Query available shares on the server
#     shares = session.list_shares()
    
#     # Assuming you want to connect to the first share found (you can iterate through 'shares' list as needed)
#     if shares:
#         share_name = shares[0].share_name
        
#         # Connect to the share
#         share_path = f"\\\\{server_ip}\\{share_name}"
#         tree = TreeConnect(session, share_path)
#         tree.connect()
        
#         # Open the root directory of the share
#         root_dir = Open(tree, "")
#         root_dir.create(
#             impersonation_level=2,
#             desired_access=0x00120089,  # GENERIC_READ | GENERIC_WRITE | FILE_READ_ATTRIBUTES
#             file_attributes=0,  # Normal file
#             share_access=7,  # FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE
#             create_disposition=1,  # FILE_OPEN
#             create_options=0x200000,  # FILE_DIRECTORY_FILE
#             create_contexts=[]
#         )

#         # List the contents of the share
#         files = root_dir.query_directory(
#             search_pattern="*",
#             file_information_class=FileInformationClass.FILE_DIRECTORY_INFORMATION,
#             output_buffer_length=65536  # Example buffer length
#         )

#         for file_info in files:
#             file_name = file_info.file_name.get_value()
#             print(file_name)

#         # Clean up
#         root_dir.close()
#         tree.disconnect()
    
#     session.disconnect()
#     connection.disconnect()

# except Exception as e:
#     print(f"An error occurred: {e}")
# # from smbprotocol.connection import Connection
# # from smbprotocol.session import Session
# # from smbprotocol.tree import TreeConnect
# # from smbprotocol.open import Open
# # from smbprotocol.file_info import FileInformationClass
# # from smbprotocol.structure import SMB2Dialect
# # import os

# # # Establish connection
# # server_ip = "192.168.2.201"
# # username = "user"
# # password = "Server@123"
# # share_name = ""

# # connection = Connection(uuid=os.urandom(16), server_name=server_ip, dialect=SMB2Dialect.SMB_2_1)
# # connection.connect()

# # # Perform session setup
# # session = Session(connection, username, password)
# # session.connect()

# # # Connect to the share
# # tree = TreeConnect(session, r"\\%s\%s" % (server_ip, share_name))
# # tree.connect()

# # # Open the root directory
# # root_dir = Open(tree, "")
# # root_dir.create()

# # # List the contents of the share
# # files = root_dir.query_directory("*")
# # for file in files:
# #     print(file['file_name'].get_value())

# # # Clean up
# # root_dir.close()
# # tree.disconnect()
# # session.disconnect()
# # connection.disconnect()

# # # import os
# # # import ctypes
# # # from smbprotocol.connection import Connection
# # # from smbprotocol.session import Session
# # # from smbprotocol.tree import TreeConnect
# # # from smbprotocol.open import CreateOptions, ImpersonationLevel, Open
# # # from smbprotocol.file_info import FileInfoClass
# # # from smbprotocol.structure import FileAttributes
# # # from smbprotocol.exceptions import SMBException

# # # # Assuming you already have WNetAddConnection2 working and connected
# # # # Here is how you can list shared folders

# # # # Define the necessary structures and constants for WNetAddConnection2
# # # class NETRESOURCE(ctypes.Structure):
# # #     _fields_ = [
# # #         ("dwScope", ctypes.c_ulong),
# # #         ("dwType", ctypes.c_ulong),
# # #         ("dwDisplayType", ctypes.c_ulong),
# # #         ("dwUsage", ctypes.c_ulong),
# # #         ("lpLocalName", ctypes.c_wchar_p),
# # #         ("lpRemoteName", ctypes.c_wchar_p),
# # #         ("lpComment", ctypes.c_wchar_p),
# # #         ("lpProvider", ctypes.c_wchar_p)
# # #     ]

# # # WNET_ADD_CONNECTION2 = ctypes.windll.mpr.WNetAddConnection2W
# # # WNET_CANCEL_CONNECTION2 = ctypes.windll.mpr.WNetCancelConnection2W

# # # # Replace with your actual values
# # # network_path = r"\\192.168.2.201\\"
# # # username = "user"
# # # password = "Server@123"

# # # # Connect using WNetAddConnection2
# # # net_resource = NETRESOURCE()
# # # net_resource.dwType = 1  # RESOURCETYPE_DISK
# # # net_resource.lpRemoteName = network_path

# # # result = WNET_ADD_CONNECTION2(ctypes.byref(net_resource), password, username, 0)
# # # if result != 0:
# # #     raise ctypes.WinError(result)

# # # # Use smbprotocol to list shared folders
# # # server_ip = "192.168.2.201"
# # # username = "user"
# # # password = "Server@123"

# # # try:
# # #     # Establish connection
# # #     connection = Connection(uuid=os.urandom(16), server_name=server_ip)
# # #     connection.connect()

# # #     # Perform session setup
# # #     session = Session(connection, username, password)
# # #     session.connect()

# # #     # Connect to the IPC$ tree to list shares
# # #     tree = TreeConnect(session, r"\\%s\IPC$" % server_ip)
# # #     tree.connect()

# # #     # Open the Lsarpc named pipe
# # #     lsarpc = Open(tree, r"lsarpc", FileAttributes.FILE_ATTRIBUTE_NORMAL)
# # #     lsarpc.create(ImpersonationLevel.Impersonation, FileAttributes.FILE_ATTRIBUTE_NORMAL, CreateOptions.FILE_NON_DIRECTORY_FILE)

# # #     # List shares
# # #     share_enum = lsarpc.query_directory(
# # #         "*",
# # #         FileInfoClass.FileNamesInformation,
# # #         None,
# # #         4096,
# # #     )

# # #     # Print share names
# # #     for share in share_enum:
# # #         print(share.file_name)

# # # except SMBException as e:
# # #     print(f"SMBException: {e}")

# # # finally:
# # #     # Clean up connections
# # #     WNET_CANCEL_CONNECTION2(network_path, 0, True)

