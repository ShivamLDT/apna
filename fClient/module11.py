
import os
import win32com.client

def export_folder_to_pst(folder_name, pst_file_path):
    # Connect to Outlook application
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    
    # Find the desired folder (e.g., Inbox)
    for i in range(outlook.Folders.Count):
        folder = outlook.Folders.Item(i + 1)
        if folder.Name == folder_name:
            break
    else:
        print(f"Folder '{folder_name}' not found.")
        return
    
    # Export the folder to a PST file
    print(f"Exporting folder '{folder_name}' to '{pst_file_path}'...")
    try:
        outlook.Folders(folder_name).ExportAsPST(pst_file_path)
        print("Export completed successfully.")
    except Exception as e:
        print(f"Failed to export folder: {e}")

# Specify the folder name and PST file path
folder_name = "hod.software@3handshake.in"  # Change to the folder you want to export
pst_file_path = os.path.expanduser("~\Desktop\exported_data.pst")

export_folder_to_pst(folder_name, pst_file_path)
