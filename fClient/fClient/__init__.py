"""
The flask application package.
"""


import socketio
from flask_compress import Compress

# from .sktiof import sktio
from flask import Flask, sessions
import sys
from werkzeug.middleware.profiler import ProfilerMiddleware

# global cl
# cl = socketio.Client()
compress = Compress()
from fClient.fingerprint  import getCodeHost,getCode,getKey,getRequestKey,get_hKey,getCodea
app = Flask(__name__)
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir=r"D:\tmp_f\flask_c_profiler")
app.config["getCode"]=getCode()
if app.config["getCode"] ==None:
    sys.exit("cannot identify the identity so exit ")
app.config["getCodea"]=getCodea()
app.config["getCodeHost"]=getCodeHost()
app.config["getKey"]=getKey()
app.config["getRequestKey"]=getRequestKey()
app.config["get_hKey"]=get_hKey() 

global  a_scheduler
compress.init_app(app)
# mdns = MDNS(app)
# skito = sktio
import fClient.ipbrd
import fClient.views
import fClient.fingerprint
import fClient.sqlite_managerA
from fClient.sqlite_managerA import SQLiteManager
from fClient.cm import CredentialManager
from fClient.unc import NetworkShare, EncryptedFileSystem
from fClient.FilesUtil import FileCollector
from fClient.p7zstd import p7zstd
from fClient.defaultResponse import post_process_context


SIGNATURE_MAP_COMPRESSION_LEVEL = {
    # Archives

    b'\x37\x7A\xBC\xAF\x27\x1C': 7, # 7z
    b'\x1F\x8B': 6,                 # GZ, TAR.GZ
    b'\x43\x61\x74\x20': 4,         # TAR - Tar Archive
    b'\x75\x73\x74\x61\x72': 4,     # TAR Archive (ustar)
    b'\x43\x44\x30\x30\x31': 5,     # ISO
    b'\x50\x4B\x03\x04': 4,         # ZIP, DOCX, XLSX, PPTX, APK, IPA
    b'\x42\x5A\x68': 4,             # BZ2 - Bzip2
    b'\x1F\x8B': 4,                 # GZ - Gzip
    b'\x52\x61\x72\x21': 4,         # RAR - RAR Archive
    b'\x37\x7A\xBC\xAF\x27\x1C': 4, # 7Z - 7-Zip
    b'\x50\x41\x52\x21': 4,         # PAR - Parity Archive
    b'\x37\x48\x64\x33': 4,         # HFS - Apple HFS Archive

    
    # DB   
    b'\x53\x51\x4C\x69': 1,                                 # SQLite (.sqlite, .db, .sqlite3)
    b'\x00\x01\x00\x00\x53\x50\x41\x52\x4B\x00\x00\x00': 1, # Microsoft Access (.mdb)
    b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 1,                 # Microsoft Access (.mdb), Excel (.xls), Word (.doc) - Compound File Binary
    b'\xFE\xED\xFE\xED': 1,                                 # Lotus Notes database (.nsf)
    b'\x7F\x45\x4C\x46': 1,                                 # ELF (used in some Unix-based systems)
    b'\xF0\x0D\xCA\xFE':1,                                  # MongoDB

    # ============> MySQL
    b'\x46\x45\x48\x00': 3,     # .ism - MySQL Index File
    b'\x4D\x59\x53\x51': 3,     # .myd - MySQL Data File
    # ============> PostgreSQL
    b'\x50\x47\x44\x42': 3,     # .pgd - PostgreSQL Data
    b'\x57\x41\x4C\x00': 3,     # WAL File
    # ============> Firebird
    b'\x46\x42\x44\x02': 3,     # .fdb - Firebird Database
    # ============> Oracle
    b'\x4F\x52\x41\x43': 3,     # Oracle DBF file
    b'\x4C\x4F\x42\x00': 3,     # Oracle LOB file
    b'\x52\x45\x44\x4F': 3,     # Oracle Redo Log   
    b'\xFF\xD8\xFF': 1,         # Oracle BLOB stored as JPEG
    b'\x0A\x00\x00\x00\x01\x00\x00\x00': 1, # Oracle datafile header (.dbf)
    b'\x03\x00\x00\x00': 1,     # Oracle tablespace header
    b'\x00\x02\x00\x00': 1,     # Oracle redo log file
    b'\xFF\xFE\x00\x00': 1,     # Oracle LOB file

    b'\x03\x00\x00\x00': 3,     # .dbf - dBase Data File   
    b'\x53\x51\x4C\x69': 3,     # .db - Sybase Database File  
    b'\x00\x00\x00\x00\x00\x00\x00\x00': 3, # MongoDB Data File  
    b'\x01\x00\x00\x00\x01\x00\x00\x00': 3, # .mdf - Primary Database
    b'\x01\x00\x00\x00\x02\x00\x00\x00': 3, # .ndf - Secondary Database
    b'\x01\x00\x00\x00\x03\x00\x00\x00': 3, # .ldf - Log File   
    b'\x01\x00\x00\x00\x01\x00\x00\x00': 3, # .mdf-based format
    b'\x50\x4B\x03\x04': 4,     # .bacpac - Azure SQL Package
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00': 1, # DB2 tablespace

    b'\x01\xAD\x00\x00': 1,     # Informix data file

    # ============> QuickBooks
    b'\x51\x42\x57\x00': 3,     # .qbw
    b'\x51\x42\x42\x00': 3,     # .qbb
    b'\x51\x42\x4D\x00': 3,     # .qbm
    # ============> Sage / Peachtree
    b'\x50\x54\x43\x00': 3,     # .ptc
    b'\x50\x54\x42\x00': 3,     # .ptb
    b'\x53\x41\x47\x45': 3,     # .sage
    b'\x44\x41\x54\x00': 3,     # .dat
    # ============> MYOB
    b'\x4D\x59\x4F\x42': 3,     # .myo 
    # ============> Xero
    b'\x58\x45\x52\x4F': 3,     # .xero
    # ============> Tally
    b'\x39\x30\x30\x00': 3,     # .900
    # ============> FreshBooks
    b'\x46\x52\x53\x48': 3,     # .fresh
    # ============> Wave
    b'\x57\x41\x56\x45': 3,     # .wave


    # Documents
    b'%PDF-': 6,       # PDF
    b'\xD0\xCF\x11\xE0': 6,     # Old MS Office (DOC, XLS, PPT)
    b'\x0A\x25\x2D\x2D\x20': 5, # PostScript
    b'\x46\x4F\x52\x4D': 5,     # AI (Adobe Illustrator)

    # Images
    b'\x89PNG\r\n\x1A\n': 1,    # PNG
    b'\x89\x50\x4E\x47': 1,     # PNG
    b'\xFF\xD8\xFF\xE0': 1,     # JPEG  
    b'\xFF\xD8\xFF': 1,         # JPG
    b'\x42\x4D': 1,             # BMP
    b'\x47\x49\x46\x38': 1,     # GIF
    b'\x49\x49\x2A\x00': 1,     # TIFF (little endian)
    b'\x4D\x4D\x00\x2A': 1,     # TIFF (big endian)

    # Audio/Video
    b'\x49\x44\x33': 1,         # MP3
    b'\x00\x00\x01\xBA': 1,     # MPEG/MPG
    b'\x00\x00\x01\xB3': 1,     # AVI
    b'\x1A\x45\xDF\xA3': 1,     # MKV
    b'RIFF': 1,                 # WAV    

    b'\x66\x74\x79\x70': 1,     # MP4
    b'\x52\x49\x46\x46': 1,     # WAV, AVI
    b'\x30\x26\xB2\x75': 1,     # WMV
    b'\x1A\x45\xDF\xA3': 1,     # MKV

    # Executables & Libraries
    b'\x4D\x5A': 1,             # EXE, DLL
    b'\x7F\x45\x4C\x46': 1,     # ELF (Linux Executable)
    b'\xCA\xFE\xBA\xBE': 1,     # Java .class files
    b'\xFE\xED\xFA\xCE': 1,     # Mach-O (macOS executables)

    # Code Files
    b'\x23\x21': 9,             # SHEBANG (Python, Shell)
    b'\x3C\x68\x74\x6D': 9,     # HTML
    b'\x3C\x73\x63\x72': 9,     # JavaScript
    b'\x7B\x0A': 9,             # JSON
    b'\x0A': 9,                 # TXT, CSV, XML

    # System Files
    b'\x5B\x53\x65\x74': 6,     # INF (Setup Info)
    b'\x49\x4E\x49\x00': 6,     # INI (Windows INI Files)

    # Adobe Proprietary
    b'\x38\x42\x50\x53': 1,     # PSD (Adobe Photoshop)
    b'\x25\x50\x44\x46\x2D': 6, # PDF (Adobe Acrobat)
    b'\x41\x49\x46\x46': 5,     # AI (Adobe Illustrator)
    b'\x46\x57\x53': 5,         # SWF (Adobe Flash)
    b'\x46\x4C\x56\x01': 3,     # FLV (Flash Video)
   
    b'\x4D\x4F\x56\x49': 4,     # MOV - QuickTime
    b'\x41\x56\x49\x20': 4,     # AVI - Premiere
    b'\x70\x72\x6F\x6A': 4,     # PRPROJ - Premiere Project
    b'\x61\x65\x73\x00': 4,     # AEP - After Effects Project

    # Corel Proprietary
    b'\x43\x44\x52\x30': 5,                     # CDR (CorelDRAW)
    b'\x4D\x53\x43\x46': 4,                     # CMX (Corel Presentation Exchange)
    b'\x57\x69\x6E\x64': 4,                     # CPT (Corel Photo-Paint)

    # Autodesk Proprietary
    b'\x49\x49\x2A\x00\x10\x00\x00\x00': 4,     # DWG (AutoCAD)
    b'\x41\x43\x31\x30': 5,                     # DXF (AutoCAD)
    b'\x4D\x45\x53\x53': 4,                     # MA (Maya)
    b'\x41\x44\x42\x4C': 4,                     # MB (Maya Binary)

    # 3D Formats
    b'\x4D\x44\x4C\x5F': 5,                     # MDL (3D Model)
    b'\x00\x00\x00\x18\x66\x74\x79\x70': 3,     # MP4 (Movie)
}
