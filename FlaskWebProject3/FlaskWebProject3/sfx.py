import zipfile
import os
import sys
import zipfile
import os
import subprocess
import sys

class ZipToSFX:
    def __init__(self, zip_file, output_sfx_name, executable_name):
        """
        Initialize the class with the zip file name, output SFX file name, and the executable name (abc.exe).
        """
        self.zip_file = zip_file
        self.output_sfx_name = output_sfx_name
        self.executable_name = executable_name

    def combine_script_and_zip(self, script_file):
        """
        Combine the Python extraction script with the zip file to create the SFX executable.
        """
        with open(self.output_sfx_name, 'wb') as sfx_file:
            # Write the extraction script to the SFX file
            with open(script_file, 'rb') as script:
                sfx_file.write(script.read())

            # Append the zip file to the SFX file
            with open(self.zip_file, 'rb') as zip_f:
                sfx_file.write(zip_f.read())
        
        print(f"Self-extracting executable {self.output_sfx_name} created.")

    @staticmethod
    def extract_and_run(archive_offset, executable_name, extract_to='.'):
        """
        Extract the zip archive embedded in this script and run the specified executable (abc.exe).
        """
        # Read the current script (self) and extract the zip data
        with open(sys.argv[0], 'rb') as f:
            f.seek(archive_offset)
            archive_data = f.read()

        # Save the embedded zip to a temporary file and extract it
        temp_zip_path = os.path.join(extract_to, 'temp_archive.zip')
        with open(temp_zip_path, 'wb') as temp_zip:
            temp_zip.write(archive_data)

        # Extract the contents of the temporary zip
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(temp_zip_path)  # Clean up the temporary zip file

        # Run the executable (abc.exe) from the extracted contents
        executable_path = os.path.join(extract_to, executable_name)
        if os.path.exists(executable_path):
            print(f"Running {executable_path}...")
            subprocess.run([executable_path])
        else:
            print(f"{executable_name} not found in the extracted files!")

    def create_sfx(self):
        """
        Create a simple extraction script, then combine it with the zip file to create the SFX.
        """
        # Generate the Python extraction script on-the-fly
        extraction_script = f"""
import zipfile
import os
import subprocess
import sys

def extract_and_run(archive_offset, executable_name, extract_to='.'):
    with open(sys.argv[0], 'rb') as f:
        f.seek(archive_offset)
        archive_data = f.read()
    
    temp_zip_path = os.path.join(extract_to, 'temp_archive.zip')
    with open(temp_zip_path, 'wb') as temp_zip:
        temp_zip.write(archive_data)

    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(temp_zip_path)

    executable_path = os.path.join(extract_to, executable_name)
    if os.path.exists(executable_path):
        print(f"Running {{executable_path}}...")
        subprocess.run([executable_path])
    else:
        print(f"{{executable_name}} not found in the extracted files!")

if __name__ == "__main__":
    extract_and_run(archive_offset={{archive_offset}}, executable_name="{self.executable_name}")
"""

        # Save the extraction script to a temporary file
        script_file = 'extractor_script.py'
        with open(script_file, 'w') as file:
            file.write(extraction_script)

        # Combine the extraction script with the zip archive to create the SFX
        self.combine_script_and_zip(script_file)

        # Clean up temporary script file
        os.remove(script_file)
        print("SFX creation completed.")

# Example Usage:
# if __name__ == "__main__":
#     zip_file = 'my_archive.zip'  # The zip file containing abc.exe
#     output_sfx_name = 'self_extractor.exe'  # The final SFX output
#     executable_name = 'abc.exe'  # The executable to run after extraction

#     # Create an instance of the class
#     sfx_creator = ZipToSFX(zip_file, output_sfx_name, executable_name)

#     # Create the SFX
#     sfx_creator.create_sfx()
