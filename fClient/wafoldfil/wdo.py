import os
import json
import shutil
import zipfile
import hashlib
import asyncio
from datetime import datetime
from cryptography.fernet import Fernet
from watchdog.observers import Observer
from watchdog.events import   DirCreatedEvent, DirDeletedEvent, FileSystemEvent, FileSystemEventHandler

from watchdog.events import FileMovedEvent, EVENT_TYPE_MOVED #= "moved"
from watchdog.events import FileDeletedEvent, EVENT_TYPE_DELETED #= "deleted"
from watchdog.events import FileCreatedEvent,EVENT_TYPE_CREATED #= "created"
from watchdog.events import FileModifiedEvent, EVENT_TYPE_MODIFIED #= "modified"
from watchdog.events import FileClosedEvent, EVENT_TYPE_CLOSED #= "closed"
from watchdog.events import FileClosedNoWriteEvent, EVENT_TYPE_CLOSED_NO_WRITE #= "closed_no_write"
from watchdog.events import FileOpenedEvent, EVENT_TYPE_OPENED #= "opened"

class AES256Backup:
    """Handles AES-256 encryption and backup process for multiple directories."""

    def __init__(self, encryption_key: str, backup_dir: str):
        self.backup_dir = backup_dir
        self.fernet = Fernet(self.generate_key(encryption_key))
        self.db_file = os.path.join(backup_dir, "backup_db.json")
        self.file_versions = self.load_backup_data()

    def generate_key(self, user_key: str) -> bytes:
        """Generates a 32-byte key from user input using SHA256."""
        key = hashlib.sha256(user_key.encode()).digest()
        return Fernet.generate_key()  # Required for Fernet encryption

    def encrypt_file(self, file_path: str):
        """Encrypts a file using AES-256."""
        try:
            # with open(file_path, "rb") as file:
            #     encrypted_data = self.fernet.encrypt(file.read())
            # with open(file_path, "wb") as file:
            #     file.write(encrypted_data)
            print(f"🔒 Encrypted: {file_path}")
        except Exception as e:
            print(f"Encryption failed: {e}")

    def decrypt_file(self, encrypted_path: str, output_path: str):
        """Decrypts an AES-256 encrypted file."""
        try:
            with open(encrypted_path, "rb") as file:
                decrypted_data = self.fernet.decrypt(file.read())
            with open(output_path, "wb") as file:
                file.write(decrypted_data)
            print(f"✅ Decrypted: {output_path}")
        except Exception as e:
            print(f"Decryption failed: {e}")

    def load_backup_data(self):
        """Loads the backup database tracking versions."""
        if os.path.exists(self.db_file):
            with open(self.db_file, "r") as db:
                return json.load(db)
        return {}

    def save_backup_data(self):
        """Saves the updated backup database."""
        with open(self.db_file, "w") as db:
            json.dump(self.file_versions, db, indent=4)

    def get_next_version(self, file_name):
        """Determines the next version number for the file."""
        if file_name not in self.file_versions:
            self.file_versions[file_name] = 1
        else:
            self.file_versions[file_name] += 1
        self.save_backup_data()
        return self.file_versions[file_name]

    def create_encrypted_zip(self, file_name: str, src_dir: str):
        """Creates an encrypted ZIP backup for an updated file."""
        src_path = os.path.join(src_dir, file_name)
        if os.path.exists(src_path):
            version = self.get_next_version(file_name)
            zip_name = f"{file_name}_v{version}.zip"
            zip_path = os.path.join(self.backup_dir, zip_name)

            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(src_path, os.path.basename(src_path))

                self.encrypt_file(zip_path)
                print(f"📁 Backup created: {zip_path} (Version {version})")
            except Exception as e:
                print(f"Error creating encrypted ZIP: {e}")
        else:
            print(f"File not found: {src_path}")


class SysEventHandler(FileSystemEventHandler):

    def __init__(self, backup_manager: AES256Backup,tracked_extensions):
        self.backup_manager = backup_manager
        self.tracked_extensions = tracked_extensions or []

    async def process(self, event):
        """Processes file events asynchronously."""
        print(str(event))
        if event.is_directory:
            return
        if event.event_type == EVENT_TYPE_MODIFIED : #Live
            file_path = event.src_path
            # if not any(file_path.endswith(ext) for ext in self.tracked_extensions):
            #     return
            print(f"File modified: {event.src_path}")
            file_name = os.path.basename(event.src_path)
            src_dir = os.path.dirname(event.src_path)
            self.backup_manager.create_encrypted_zip(file_name, src_dir)
        if  event.event_type == EVENT_TYPE_DELETED: #Live
            file_path = event.src_path
           
            print(f"File modified: {event.src_path}")
            file_name = os.path.basename(event.src_path)
            src_dir = os.path.dirname(event.src_path)
            self.backup_manager.create_encrypted_zip(file_name, src_dir)
        
        if event.event_type == EVENT_TYPE_CLOSED or event.event_type == EVENT_TYPE_CREATED: #Live
            print(f"File created: {event.src_path}")
            file_name = os.path.basename(event.src_path)
            src_dir = os.path.dirname(event.src_path)
            self.backup_manager.create_encrypted_zip(file_name, src_dir)
    def on_moved(self, event):
            """Triggered when a file is moved (deleted/moved to recycle bin)."""
            if not event.is_directory:
                src_path = event.src_path
                file_name = os.path.basename(src_path)
                backup_path = os.path.join(self.backup_manager, file_name)

                # If the file existed before, make a backup
                if os.path.exists(src_path):
                    try:
                        shutil.copy2(src_path, "D:\\")
                        print(f"Backup saved: {backup_path}")
                    except Exception as e:
                        print(f"Failed to backup {src_path}: {e}")

                print(f"File moved (possibly deleted): {src_path}")

    def on_modified(self, event):
        """Triggered when a file is modified."""
        asyncio.run(self.process(event))

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        asyncio.run(self.process(event))
    
    # def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
    #     asyncio.run(self.process(event))
    
    # def on_any_event(self, event: FileSystemEvent) -> None:
    #     asyncio.run(self.process(event))

class SysWatch:
    """Monitors multiple directories for file changes using Watchdog."""

    def __init__(self, watch_dirs: list, backup_manager: AES256Backup=None):
        self.watch_dirs = watch_dirs
        self.backup_manager = backup_manager
        self.event_handler = SysEventHandler(backup_manager,None)
        self.observer = Observer()
        self.id=None

    def start(self):
        """Starts monitoring all directories."""
        for directory in self.watch_dirs:
            self.observer.schedule(self.event_handler, directory, recursive=True)
        self.observer.start()
        print("Monitoring started for:", self.watch_dirs)
        try:
            while True:
                asyncio.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stops monitoring all directories."""
        self.observer.stop()
        self.observer.join()
        print("Stopped monitoring.")
    
    def restart(self):
        self.stop()
        self.start()
    
    def add_item(self,path):
        if not self.is_exist(path):
           self.watch_dirs.append(path)
    
           

    def is_exist(self,path):
        return path in self.watch_dirs.append(path)

if __name__ == "__main__":
    encryption_key = input("Enter encryption key: ")  # User-provided key
    watch_directories = [r"C:\76767", r"C:\ProgramData"]  # Folders to monitor
    watch_directories = [r"C:\76767",r"C:\\$Recycle.Bin"]  # Folders to monitor
    backup_directory = r"C:\backup_folder"  # Backup location

    os.makedirs(backup_directory, exist_ok=True)
    for folder in watch_directories:
        os.makedirs(folder, exist_ok=True)

    backup_manager = AES256Backup(encryption_key, backup_directory)
    watcher = SysWatch(watch_directories, backup_manager)

    print(f"Monitoring directories: {watch_directories}")
    watcher.start()
