import os
import shutil
import win32com.client

def create_snapshot(volume="C:\\"):
    backup = win32com.client.Dispatch("VSS.VSSCoordinator")
    backup.InitializeForBackup()
    backup.SetContext(0x00000013)  # VSS_CTX_ALL

    snapshot_set_id = backup.StartSnapshotSet()
    snapshot_id = backup.AddToSnapshotSet(volume)
    backup.PrepareForBackup()
    backup.DoSnapshotSet()

    snap_info = backup.QuerySnapshots()
    for snap in snap_info:
        if snap.OriginalVolumeName.startswith(volume):
            return snap.SnapshotDeviceObject

    return None

def copy_from_snapshot(snap_path, target_path):
    src = os.path.join(snap_path, "Users")  # Example
    dst = os.path.join(target_path, "SnapshotExport")
    shutil.copytree(src, dst)

if __name__ == "__main__":
    snap_root = create_snapshot("C:\\")
    if snap_root:
        print("[+] Snapshot root:", snap_root)
        copy_from_snapshot(snap_root, "D:\\Exports")
    else:
        print("[-] Failed to create snapshot.")

