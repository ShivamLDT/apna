@echo off
set FLASK_PORT=53335
set SSL_PORT=53236
set CERT_FILE=certs\cert.pem
set KEY_FILE=certs\key.pem
set FLASK_APP=runserver.py

REM Step 1: Generate self-signed cert if missing
IF NOT EXIST %CERT_FILE% (
    echo Generating self-signed certificate...
    openssl req -x509 -newkey rsa:2048 -nodes -keyout %KEY_FILE% -out %CERT_FILE% -days 1 -subj "/C=US/ST=State/L=City/O=MyOrg/OU=Dev/CN=localhost"
)

REM notepad certs\key.pem

REM Step 2: Start Flask app in background
REM echo Starting Flask app on port %FLASK_PORT%...
REM start env\scripts\python runserver --host=127.0.0.1 --port=%FLASK_PORT%"
REM timeout /t 2 > nul

REM Step 3: Start OpenSSL s_server
echo Starting OpenSSL s_server on https://localhost:%SSL_PORT%...
openssl s_server -accept %SSL_PORT% -cert %CERT_FILE% -key %KEY_FILE% -quiet -proxy 127.0.0.1:%FLASK_PORT%

REM Step 4: Stop Flask server on exit
echo.
echo Press any key to close.
pause > nul
