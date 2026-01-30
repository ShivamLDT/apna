import subprocess

def enable_windows_time_sync():
    try:
        subprocess.run(["reg", "add", r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Parameters",
                        "/v", "NtpServer", "/t", "REG_SZ", "/d", "time.windows.com", "/f"], check=True, shell=False)
        subprocess.run(["reg", "add", r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient",
                        "/v", "Enabled", "/t", "REG_DWORD", "/d", "1", "/f"], check=True, shell=False)

        subprocess.run(["sc", "config", "w32time", "start= auto"], check=True, shell=False)
        subprocess.run(["net", "start", "w32time"], check=True, shell=False)

        subprocess.run(["w32tm", "/resync"], check=True, shell=False)

        print("Automatic time synchronization enabled with time.windows.com")
    except subprocess.CalledProcessError as e:
        print(f"Failed to enable time sync: {e}")

def set_time_zone(timezone="India Standard Time"):
    """Set the system time zone to a specified time zone (default: UTC+5:30 IST)."""
    try:
        subprocess.run(["tzutil", "/s", timezone], check=True, shell=False)
        print(f"Time zone set to {timezone}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set time zone: {e}")
