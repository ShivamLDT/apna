
# # import psutil

# # # List of system accounts you want to check against
# # SYSTEM_ACCOUNTS = ["SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE"]

# # def detect_process_account(process_name):
# #     for proc in psutil.process_iter(['pid', 'name', 'username']):
# #         try:
# #             # Check if the process name matches
# #             print("===========================================")
# #             #if process_name.lower() in proc.info['name'].lower():
# #             username = proc.info['username']
# #             if any(account in username.upper() for account in SYSTEM_ACCOUNTS):
# #                 print(f"Process '{proc.info['name']}' is running under a system account: {username}")
# #             else:
# #                 print(f"Process '{proc.info['name']}' is running under user account: {username}")
# #         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
# #             pass

# # # Replace with the process name of your exe
# # detect_process_account("your_exe_name.exe")

# import psutil
# import win32api
# import win32security
# import win32con
# import pywintypes

# def get_process_username(pid):
#     try:
#         # Get a handle to the process with the necessary permissions
#         process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)

#         # Get the security token of the process
#         token_handle = win32security.OpenProcessToken(process_handle, win32security.TOKEN_QUERY)

#         # Get the user information from the token
#         user_sid = win32security.GetTokenInformation(token_handle, win32security.TokenUser)[0]

#         # Convert SID to a readable account name
#         account_name, domain, _ = win32security.LookupAccountSid(None, user_sid)
#         return f"{domain}\\{account_name}"

#     except (pywintypes.error, psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
#         return f"Could not retrieve user for process: {str(e)}"

# def detect_process_account(process_name):
#     for proc in psutil.process_iter(['pid', 'name']):
#         try:
#             # Check if the process name matches
#             if process_name.lower() in proc.info['name'].lower():
#                 username = get_process_username(proc.info['pid'])
#                 print(f"Process '{process_name}' is running under account: {username}")
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
#             print(f"Could not retrieve user for process {proc.info['name']}: {str(e)}")

# # Replace with the process name of your exe (e.g., chrome.exe)
# detect_process_account("chrome.exe")
