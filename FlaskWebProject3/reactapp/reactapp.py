import json
import platform
import socket
import os

class ReactProxyReplacer2:
    def __init__(self, project_directory, old_proxy_value="192.168.2.201",new_proxy_value=None):
        self.project_directory = project_directory
        self.old_proxy_value = old_proxy_value
        if new_proxy_value == None:
            self.new_proxy_value = self.get_local_ip()            
        else:
            self.new_proxy_value = new_proxy_value

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 135))
        ip = s.getsockname()[0]
        s.close()
        system_info = platform.uname()
        local_ip = ip         
        return ip

    def replace_proxy_in_file(self, file_path):
        file_data=""
        try:
            with open(file_path, 'r') as file:
                file_data = file.read()
        except:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                file_data = file.read()


        if self.old_proxy_value in file_data:
            file_data = file_data.replace(self.old_proxy_value+":", self.new_proxy_value+":")
            try:
                with open(file_path, 'w') as file:
                    file.write(file_data)
            except:
                with open(file_path, 'w', encoding='utf-8', errors='replace') as file:
                    file.write(file_data)
            #print(f"Updated proxy in {file_path} to {self.new_proxy_value}")
        return

    def replace_proxy_in_directory(self):
        for root, _, files in os.walk(self.project_directory):
            for file in files:
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.html')):  # Add other relevant file extensions
                    file_path = os.path.join(root, file)
                    self.replace_proxy_in_file(file_path)
        return

class ReactAppProxyUpdater:
    def __init__(self, package_json_path):
        self.package_json_path = package_json_path
        self.local_ip = self.get_local_ip()

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 135))
        ip = s.getsockname()[0]
        s.close()
        system_info = platform.uname()
        local_ip = ip 
        return ip

    def update_proxy(self):
        try:
            with open(self.package_json_path, 'r') as file:
                package_data = json.load(file)
                
            package_data['proxy'] = f"http://{self.local_ip}:3000"
            
            with open(self.package_json_path, 'w') as file:
                json.dump(package_data, file, indent=2)
            
            print(f"Updated proxy to http://{self.local_ip}:3000")
        
        except FileNotFoundError:
            print(f"Error: {self.package_json_path} not found.")
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

# if __name__ == '__main__':
#     updater = ReactAppProxyUpdater('package.json')
#     updater.update_proxy()
