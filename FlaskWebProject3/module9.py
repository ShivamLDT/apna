# from shutil import copytree
# import sys
# import os
# import threading
# import time
# import pywintypes
# import win32wnet


# CONNECT_INTERACTIVE = 0x00000008

# HOST_NAME ="192.168.2.201"
# SHARE_NAME = ""
# SHARE_FULL_NAME = os.path.sep * 2 + os.path.sep.join((HOST_NAME, SHARE_NAME))
# SHARE_USER = "user"
# SHARE_PWD = "Server@123"


# def main():
#     net_resource = win32wnet.NETRESOURCE()
#     net_resource.lpRemoteName = SHARE_FULL_NAME
#     flags = 0
#     # flags |= CONNECT_INTERACTIVE
#     print("Trying to create connection to: {:s}".format(SHARE_FULL_NAME))
#     try:
#         win32wnet.WNetCancelConnection2(SHARE_FULL_NAME, 0, 0)
#     except:
#         pass

#     try:
#         win32wnet.WNetAddConnection2(net_resource, SHARE_PWD, SHARE_USER, flags)
#     except pywintypes.error as e:
#         print(e)
#     else:
#         print("Success!")
#         import os

#         t1 = time.time()
#         #copytree("c:\\nginx-1.25.3",os.path.join( SHARE_FULL_NAME,"nginx-1.25.3"))
#         for a, b, c in os.walk(SHARE_FULL_NAME):
#             for bc in b:
#                 # threading.Thread(
#                 #     #target=copytree(os.path.join(a, bc), os.path.join("C:\\txta\\", bc))
#                 # target=print(os.path.join(a, bc))
#                 # ).start()
#                 print(os.path.join(a, bc))
#             break
#         print(time.time() - t1)
#     try:
#         win32wnet.WNetCancelConnection2(SHARE_FULL_NAME, 0, 0)
#     except:
#         pass


# if __name__ == "__main__":
#     print("Python {:s} on {:s}\n".format(sys.version, sys.platform))
#     main()
