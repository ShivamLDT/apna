import os
import socket
import subprocess
import platform

class AutoSSL:
    def __init__(self, cert_dir="certs"):
        """Initialize the AutoSSL class and generate/trust SSL certificates."""
        self.cert_dir = cert_dir
        self.lan_ip = self.get_lan_ip()
        self.cert_file, self.key_file = self.generate_and_trust_cert()

    def get_lan_ip(self):
        """Detect the LAN IP dynamically."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def trust_certificate(self, cert_file):
        """Automatically trust the SSL certificate on Windows, macOS, and Linux."""
        system = platform.system()

        if system == "Windows":
            print(" Adding certificate to Windows Trusted Root Store...")
            subprocess.run(f'certutil -addstore "Root" "{cert_file}"', shell=False, check=True)

        elif system == "Darwin":  # macOS
            print(" Adding certificate to macOS System Keychain...")
            subprocess.run(f'sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "{cert_file}"', shell=False, check=True)

        elif system == "Linux":
            print(" Adding certificate to Linux Trusted Store...")
            cert_store_path = "/usr/local/share/ca-certificates/"
            os.makedirs(cert_store_path, exist_ok=True)
            trusted_cert_path = os.path.join(cert_store_path, "flask_cert.crt")

            subprocess.run(f"sudo cp {cert_file} {trusted_cert_path}", shell=False, check=True)
            subprocess.run("sudo update-ca-certificates", shell=False, check=True)

        print(" Certificate is now trusted by the OS!")

    def generate_and_trust_cert(self):
        """Generate a self-signed certificate with Subject Alternative Names (SAN) and trust it."""
        cert_file = os.path.join(self.cert_dir, f"cert_{self.lan_ip}.pem")
        key_file = os.path.join(self.cert_dir, f"key_{self.lan_ip}.pem")
        config_file = os.path.join(self.cert_dir, "openssl.cnf")

        os.makedirs(self.cert_dir, exist_ok=True)

        if os.path.exists(cert_file) and os.path.exists(key_file):
            self.trust_certificate(cert_file)
            return cert_file, key_file

        print(f" Generating SSL certificate for {self.lan_ip} with SAN...")

        # Generate OpenSSL config with SAN
        openssl_config = f"""
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = {self.lan_ip}

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
IP.1 = {self.lan_ip}
IP.2 = 127.0.0.1
"""
        with open(config_file, "w") as f:
            f.write(openssl_config)

        # Generate SSL Certificate
        cmd = f"""openssl req -x509 -newkey rsa:2048 -keyout {key_file} -out {cert_file} -days 365 -nodes -config {config_file}"""
        subprocess.run(cmd, shell=False, check=True)

        self.trust_certificate(cert_file)
        return cert_file, key_file

    def get_cert_files(self):
        """Return the certificate and key file paths."""
        return self.cert_file, self.key_file
