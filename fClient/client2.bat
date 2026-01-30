Scripts\pyinstaller.exe -n abc --dist \Client20032020_1751 -i Abl.jpeg --onefile ..\..\fClient\runserver.py --clean  --runtime-tmpdir=.  --hidden-import win32timezone --hidden-import tzdata --version-file=..\..\fClient\clientVer.txt

copy "D:\Client20032020_1751\Output\endpoint\ApnaBackup Endpoint.exe"  "D:\Client20032020_1751\Output\endpoint\Client20032020_1751.exe"

copy "D:\Client20032020_1751\Output\endpoint\Client20032020_1751.exe"  ..\downloads\Client20032020_1751.exe

Scripts\pyinstaller.exe -n abs --dist \Server20032020_1751  -i absr.png  --onefile ..\runserver.py --clean  --runtime-tmpdir=.  --hidden-import win32timezone --hidden-import flask_socketio --hidden-import python_socketio --add-data "..\FlaskWebProject3\templates;templates"  --add-data "..\FlaskWebProject3\static;static"  --add-data "D:\ApnaBackupReactAppBuild;rapp"   --add-data "D:\Client20032020_1751\Output\endpoint;downloads" --version-file ..\server_Ver.txt
