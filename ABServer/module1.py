import psutil

# List of system accounts you want to check against
SYSTEM_ACCOUNTS = ["SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE"]

def detect_process_account(process_name):
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            # Check if the process name matches
            if process_name.lower() in proc.info['name'].lower():
                username = proc.info['username']
                if any(account in username.upper() for account in SYSTEM_ACCOUNTS):
                    print(f"Process '{process_name}' is running under a system account: {username}")
                else:
                    print(f"Process '{process_name}' is running under user account: {username}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# Replace with the process name of your exe
detect_process_account("your_exe_name.exe")

