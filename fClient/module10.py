import argparse
import win32com.client

import win32com.client
import os

# class ShadowCopy:
#     def __init__(self, drive_letters):
#         """
#         Creates shadow copies for each local drive in the provided set of drive_letters.
#         """
#         self.__drive_letters = set()
#         self.__shadow_ids = {}
#         self.__shadow_paths = {}

#         try:
#             self.wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
#         except Exception as e:
#             raise RuntimeError(f"Failed to connect to WMI: {e}")

#         for dl in drive_letters:
#             self.__add_drive(dl.upper())

#     def shadow_path(self, path):
#         """Converts a regular file system path to its equivalent shadow copy path."""
#         if not os.path.isabs(path):
#             raise ValueError(f"Path must be absolute: {path}")

#         drive_letter = path[0].upper()
#         if drive_letter in self.__drive_letters:
#             return path.replace(drive_letter + ':', self.__shadow_paths[drive_letter], 1)
#         else:
#             raise RuntimeError(f"No shadow copy found for drive {drive_letter}")

#     def delete(self):
#         """Deletes all shadow copies created by this instance."""
#         for shadow_id in list(self.__shadow_ids.values()):
#             self.__vss_delete(shadow_id)
#         self.__drive_letters.clear()
#         self.__shadow_ids.clear()
#         self.__shadow_paths.clear()

#     def __add_drive(self, drive_letter):
#         """Adds a drive to the shadow copy management system."""
#         if drive_letter in self.__drive_letters:
#             return
#         try:
#             shadow_id = self.__vss_create(drive_letter)
#             shadow_path = self.__vss_list(shadow_id)
#             self.__drive_letters.add(drive_letter)
#             self.__shadow_ids[drive_letter] = shadow_id
#             self.__shadow_paths[drive_letter] = shadow_path
#         except Exception as e:
#             raise RuntimeError(f"Failed to create shadow copy for {drive_letter}: {e}")

#     def __vss_get_id(self, shadow_id):
#         """Retrieves shadow copy information based on its ID."""
#         query = f"SELECT * FROM Win32_ShadowCopy WHERE ID='{shadow_id}'"
#         results = self.wmi.ExecQuery(query)
#         if not results:
#             raise RuntimeError(f"Shadow copy ID not found: {shadow_id}")
#         return results[0]

#     def __vss_list(self, shadow_id):
#         """Retrieves the shadow copy path for a given shadow ID."""
#         return self.__vss_get_id(shadow_id).DeviceObject

#     def __vss_create(self, drive_letter):
#         """Creates a shadow copy for the specified drive letter."""
#         try:
#             sc = self.wmi.Get("Win32_ShadowCopy")
#             create_params = sc.Methods_("Create").InParameters.SpawnInstance_()
#             create_params.Properties_("Volume").Value = f"{drive_letter}:\\"
#             results = sc.ExecMethod_("Create", create_params)
#             return results.Properties_("ShadowID").Value
#         except Exception as e:
#             raise RuntimeError(f"Shadow copy creation failed for {drive_letter}: {e}")

#     def __vss_delete(self, shadow_id):
#         """Deletes a shadow copy based on its ID."""
#         try:
#             shadow_info = self.__vss_get_id(shadow_id)
#             shadow_info.Delete_()
#         except Exception as e:
#             raise RuntimeError(f"Failed to delete shadow copy {shadow_id}: {e}")
################################

class ShadowCopy:
    def __init__(self, drive_letters):
        """
        Creates shadow copies for each local drive in the provided set of drive_letters.
        """
        self.__drive_letters = set()
        self.__shadow_ids = {}
        self.__shadow_paths = {}

        try:
            self.wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to WMI: {e}")

        for dl in drive_letters:
            self.__add_drive(dl.upper())

    def shadow_path(self, path):
        """
        Converts a regular file system path to its equivalent shadow copy path.
        """
        import os
        if not os.path.isabs(path):
            raise ValueError(f"Path must be absolute: {path}")

        drive_letter = path[0].upper()
        if drive_letter in self.__drive_letters:
            shadow_prefix = self.__shadow_paths[drive_letter]
            new_path = path.replace(drive_letter + ':', shadow_prefix, 1)
            if new_path == path:
                raise RuntimeError(f"Failed to convert path: {path}")
            return new_path
        else:
            raise RuntimeError(f"No shadow copy found for drive {drive_letter}")

    def unshadow_path(self, path):
        """
        Converts a shadow copy path to its equivalent regular file system path.
        """
        for dl, sp in self.__shadow_paths.items():
            if sp in path:
                new_path = path.replace(sp, dl + ":", 1)
                if new_path == path:
                    raise RuntimeError(f"Failed to convert shadow path: {path}")
                return new_path
        raise RuntimeError("No matching drive letter found for shadow path")

    def delete(self):
        """
        Deletes all shadow copies created by this instance.
        """
        for shadow_id in list(self.__shadow_ids.values()):
            self.__vss_delete(shadow_id)
        self.__drive_letters.clear()
        self.__shadow_ids.clear()
        self.__shadow_paths.clear()

    def __add_drive(self, drive_letter):
        """
        Adds a drive to the shadow copy management system.
        """
        if drive_letter in self.__drive_letters:
            return  # Already added

        try:
            shadow_id = self.__vss_create(drive_letter)
            shadow_path = self.__vss_list(shadow_id)
            self.__drive_letters.add(drive_letter)
            self.__shadow_ids[drive_letter] = shadow_id
            self.__shadow_paths[drive_letter] = shadow_path
        except Exception as e:
            raise RuntimeError(f"Failed to create shadow copy for {drive_letter}: {e}")

    def __vss_get_id(self, shadow_id):
        """
        Retrieves shadow copy information based on its ID.
        """
        query = f"SELECT * FROM Win32_ShadowCopy WHERE ID='{shadow_id}'"
        results = self.wmi.ExecQuery(query)
        if not results:
            raise RuntimeError(f"Shadow copy ID not found: {shadow_id}")
        return results[0]

    def __vss_list(self, shadow_id):
        """
        Retrieves the shadow copy path for a given shadow ID.
        """
        shadow_info = self.__vss_get_id(shadow_id)
        return shadow_info.DeviceObject

    def __vss_create(self, drive_letter):
        """
        Creates a shadow copy for the specified drive letter.
        """
        try:
            sc = self.wmi.Get("Win32_ShadowCopy")
            create_params = sc.Methods_("Create").InParameters.SpawnInstance_()
            create_params.Properties_("Volume").Value = f"{drive_letter}:\\"
            results = sc.ExecMethod_("Create", create_params)
            return results.Properties_("ShadowID").Value
        except Exception as e:
            raise RuntimeError(f"Shadow copy creation failed for {drive_letter}: {e}")

    def __vss_delete(self, shadow_id):
        """
        Deletes a shadow copy based on its ID.
        """
        try:
            shadow_info = self.__vss_get_id(shadow_id)
            shadow_info.Delete_()
        except Exception as e:
            raise RuntimeError(f"Failed to delete shadow copy {shadow_id}: {e}")

class ShadowOpen:
    """Context manager to replace the built-in open function for shadow copies."""
    def __init__(self, shadow_copy: ShadowCopy, file_path, mode='r', *args, **kwargs):
        self.shadow_copy = shadow_copy
        self.file_path = shadow_copy.shadow_path(file_path)
        self.mode = mode
        self.args = args
        self.kwargs = kwargs
        self.file = None

    def __enter__(self):
        self.file = open(self.file_path, self.mode, *self.args, **self.kwargs)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.close()
        if 'w' in self.mode or 'a' in self.mode or 'x' in self.mode:
            try:
                os.remove(self.file_path)
            except Exception as e:
                print(f"Warning: Unable to remove temporary shadow file {self.file_path}: {e}")


# if __name__ == "__main__":
#     import sys

    
#     # try:
#     #     # Create shadow copies for drives C: and D:
#     #     sc = ShadowCopy(drive_letters=["C", "D"])
        
#     #     # Example path conversion
#     #     shadow_file_path = sc.shadow_path(r"C:\path\to\file.txt")
#     #     print(f"Shadow file path: {shadow_file_path}")
        
#     #     # Clean up shadow copies
#     #     sc.delete()
#     #     print("Shadow copies deleted successfully.")
#     # except Exception as e:
#     #     print(f"Error: {e}")





# # # Create a set that contains the LOCAL disks you want to shadow
# # local_drives = set()
# # local_drives.add('C')

# # # Initialize the Shadow Copies
# # sc = ShadowCopy(local_drives)

# # # An open and locked file we want to read
# # locked_file = r'C:\Users\user\Documents\Outlook Files\hod.software@3handshake.in.pst'
# # shadow_path = sc.shadow_path(locked_file)

# # # shadow_path will look similar to:
# # # u'\\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy7\\foo\\bar.txt'

# # # Open shadow_path just like a regular file
# # with open(shadow_path, 'rb') as fp:
# #   data = fp.read()
# #   print(data)


# # # When done, clean up the shadow copies
# # sc.delete()