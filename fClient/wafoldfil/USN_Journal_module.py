import os
import time
import shutil
import psutil
import win32com.client
import win32file

# Backup directory (change as needed)
BACKUP_DIR = "C:\\BackupDeletedFiles"

def get_recycle_bin_files():
    """Returns a dictionary of files currently in the Recycle Bin."""
    shell = win32com.client.Dispatch("Shell.Application")
    recycle_bin = shell.Namespace(10)  # 10 = Recycle Bin

    deleted_files = {}
    for item in recycle_bin.Items():
        original_path = item.Path  # Original file location before deletion
        deleted_files[original_path] = item.Name  # File name
    return deleted_files

def backup_file(file_path):
    """Copies a deleted file to backup before it's permanently lost."""
    if os.path.exists(file_path):
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f" Backup saved: {backup_path}")
        except Exception as e:
            print(f" Failed to backup {file_path}: {e}")

def monitor_recycle_bin():
    """Monitors the Recycle Bin for new deletions."""
    known_files = get_recycle_bin_files()
    print(" Monitoring Recycle Bin & Permanent Deletions...")

    while True:
        time.sleep(2)  # Poll every 2 seconds

        current_files = get_recycle_bin_files()
        new_deletions = {k: v for k, v in current_files.items() if k not in known_files}

        for path, name in new_deletions.items():
            print(f"🗑 File Deleted (Recycle Bin): {name} (Original Path: {path})")
            backup_file(path)  # Backup before it's lost

        known_files = current_files  # Update known files

def monitor_permanent_deletions():
    """Uses NTFS USN Journal to detect Shift+Del (permanent) deletions."""
    drive = "C:\\"  # Track C:\ drive (change for other drives)

    # Open volume
    handle = win32file.CreateFile(
        f"\\\\.\\{drive[0]}:",
        win32file.GENERIC_READ,
        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
        None,
        win32file.OPEN_EXISTING,
        0,
        None,
    )

    usn_journal_data = win32file.DeviceIoControl(
        handle,
        0x00090064,  # FSCTL_QUERY_USN_JOURNAL
        None,
        1024,
    )

    print(" Monitoring for Shift+Del (Permanent Deletions)...")

    while True:
        time.sleep(2)  # Poll every 2 seconds

        for partition in psutil.disk_partitions():
            if partition.fstype == "NTFS":
                try:
                    # Scan USN Journal for recent deletions
                    files = os.listdir(partition.mountpoint)
                    deleted_files = [f for f in files if not os.path.exists(f)]
                    
                    for file in deleted_files:
                        print(f"File Permanently Deleted: {file}")
                        # Can't backup Shift+Del files (they're destroyed), but can log them
                except:
                    pass

try:
    from threading import Thread

    # Run both monitoring tasks in parallel
    Thread(target=monitor_recycle_bin, daemon=True).start()
    Thread(target=monitor_permanent_deletions, daemon=True).start()

    while True:
        time.sleep(1)  # Keep script alive

except KeyboardInterrupt:
    print("\n Stopping monitoring...")


