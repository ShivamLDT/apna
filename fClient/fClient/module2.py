from gzpks import GzipFileHandler

gzip_file_handler = GzipFileHandler('D:\\ApnaBackup\\e67bd65687a3391c20bf93c3b587901b9c82050f4c86b465d0a5ec8f776d11e2\\C{{DRIVE}}\\appverifUI.dll_0.gz_1715339340.3193176.gz')
output_directory = 'C:\\'
target_file_name = 'appverifUI.dll'

gzip_file_handler.decompress_file(target_file_name, output_directory)
