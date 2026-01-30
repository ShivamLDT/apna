# import os
# import base64
# from cryptography.hazmat.primitives.ciphers.aead import XChaCha20Poly1305

# def start_file_streaming(
#     file_name,
#     file,
#     root,
#     trg_folder,
#     p_name,
#     repo,
#     authId,
#     job_Start,
#     ftype,
#     p_NameText,
#     p_IdText,
#     currentfile,
#     totalfiles,
#     bkupType="full",
#     chunk_size=1024 * 1024 * 64,
#     src_location="",
#     accuracy=0.00,
#     finished=False,
#     OpendedSh = None,
#     tfi= None,
# ):


#     from fClient.cktio import cl_socketio_obj
    
#     from fClient.p7zstd import p7zstd
    
#     open_file_name =file_name
#     if OpendedSh:
#         open_file_name = OpendedSh.get_path( file_name)
#         if not open_file_name:
#             open_file_name =file_name

#     url = f"http://{app.config['server_ip']}:{app.config['server_port']}/upload"
#     try:
#         if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
#         if not cl_socketio_obj.connected:
#             try:
#                 cl_socketio_obj.connect(f"http://{app.config['server_ip']}:{app.config['server_port']}"
#                     ,wait_timeout=5
#                     ,retry=True
#                 )
#             except:
#                 print("")
#     except:
#         pass
#     seq_num = 0
#     headers = {}
#     files_dict=[]
#     try:
#         file_stat = os.stat(file_name)
#         st_ino =file_stat.st_ino
#         result=None
#         file_stat_remote = get_remote_file_stat(backup_pid =p_IdText,file_name=file_name)
#         file_stat_remote = file_stat_remote.get('result',None)
#         compressed_data = None
#         SENTINEL_NO_CHANGE = None
        
#         bOpen= True #bkupType == "full"
#         remote_first_time=0
#         remote_last_time=0
#         if file_stat_remote:
#             result = list(filter(lambda d: d.get('file_path_name').lower() == file_name.lower(), file_stat_remote))
#             if result:
#                 if bkupType == "full" :
#                     bOpen=True
#                 if bkupType == "incremental":
#                     result=result[0]
#                     bOpen=False
#                 if bkupType == "differential":
#                     result=result[1]
#                     bOpen=False
#             else:
#                 bOpen=True
        
#         if bkupType == "full":
#             bOpen=True
#         elif bkupType == "incremental":
#             print(f"perform incremental backup of this file : {file_name} ")
#             if result:
#                 if result.get('last_c',0) <= file_stat.st_mtime :
#                     bOpen=True
            
#         elif bkupType == "differential":
#             print(f"perform differential backup of this file : {file_name} ")
#             if result:
#                 if result.get('first_c',None)<=file_stat.st_mtime:
#                     bOpen=True

#         t_c = math.ceil(os.path.getsize(file_name) / chunk_size)
#         chunks = []

#         s_7z_iv = "00000000000000000000000000000000"



#         j = app.apscheduler.get_job(id=p_IdText)
#         if j != None:
#             while not j.next_run_time:
#                 try:
#                     if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
#                     if not cl_socketio_obj.connected:
#                         cl_socketio_obj.connect(
#                             f"ws://{app.config['server_ip']}:{app.config['server_port']}"
#                             ,wait_timeout=5
#                             ,retry=True             
#                         )
#                     time.sleep(2)
#                     if cl_socketio_obj.connected:
#                         cl_socketio_obj.emit(
#                             "backup_data",
#                             json.dumps(
#                                 {
#                                     "backup_jobs": [
#                                         {
#                                             "name": p_NameText,
#                                             "scheduled_time": datetime.datetime.fromtimestamp(
#                                                 float(job_Start)
#                                             ).strftime(
#                                                 "%H:%M:%S"
#                                             ),
#                                             "agent": str(app.config.get("getCodeHost",None)),
#                                             "progress_number": float(
#                                                 100 * (float(currentfile))
#                                             )
#                                             / float(totalfiles),
#                                             "accuracy": accuracy,
#                                             "finished": finished,                                            
#                                             "id": job_Start,
#                                         }
#                                     ]
#                                 }
#                             ),
#                             "/",
#                         )
#                         if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
#                 except Exception as ex:
#                     print(str(ex))
#                     try:
#                         if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
#                     except:
#                         pass
#                 time.sleep(10)
#                 j = app.apscheduler.get_job(id=p_IdText)

#         compression_level=3
#         digest=None
#         shm=None
#         num_chunks=0 
#         file_size=0

#         with open(open_file_name, "rb") as f: #m_file:
           
#             file_size = os.path.getsize(open_file_name)
#             j = app.apscheduler.get_job(id=p_IdText)
#             if j != None:
#                 while not j.next_run_time:
#                     try:
#                         if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
#                         if not cl_socketio_obj.connected:
#                             cl_socketio_obj.connect(
#                                 f"ws://{app.config['server_ip']}:{app.config['server_port']}"
#                                 ,wait_timeout=5
#                                 ,retry=True
#                             )
#                         if cl_socketio_obj.connected:
#                             cl_socketio_obj.emit(
#                                 "backup_data",
#                                 {
#                                     "backup_jobs": [
#                                         {
#                                             "status": "progress",
#                                             "name": p_NameText,
#                                             "scheduled_time": datetime.datetime.fromtimestamp(
#                                                 float(job_Start)
#                                             ).strftime(
#                                                 "%H:%M:%S"
#                                             ),
#                                             "agent": str(app.config.get("getCodea",None)),
#                                             "progress_number": float(
#                                                 100 * (float(currentfile))
#                                             )
#                                             / float(totalfiles),                                            
#                                             "accuracy": accuracy,
#                                             "finished": finished,
#                                             "id": job_Start,
#                                         }
#                                     ]
#                                 },
#                             )
#                         time.sleep(10)
#                     except:
#                         pass 
#                     j = app.apscheduler.get_job(id=p_IdText)
#             f.seek(0)
#             if bOpen:
#                 file_signature = f.read(16)
#                 compression_level = SIGNATURE_MAP_COMPRESSION_LEVEL.get(file_signature[:4], 3) or 1   
#                 if file_size < 1 * 1024 * 1024:   # < 1 MB ==> Max compression
#                     compression_level = min(compression_level + 3, 9)
#                 elif file_size < 100 * 1024 * 1024: # < 100 MB ==> High compression
#                     compression_level = min(compression_level + 2, 9)
#                 elif file_size < 1 * 1024 * 1024 * 1024: # < 1 GB ==> Medium compression
#                     compression_level = compression_level
#                 else:  # > 1 GB ==> Fast compression
#                     compression_level = max(compression_level - 2, 1)

#                 f.seek(0)

#                 chunk_size = get_optimal_chunk_size(file_size=file_size)
#                 num_chunks=math.ceil( file_size/chunk_size)
#                 compressed_data =num_chunks !=0
#                 t_c = math.ceil(file_size / chunk_size)
#             f.close()
#         if not bOpen:
#             num_chunks=1

#             SENTINEL_NO_CHANGE = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
#         if compressed_data!=None or SENTINEL_NO_CHANGE!=None:
#             if repo in ["GDRIVE", "LAN", "LOCAL", "LOCAL STORAGE","AWSS3","AZURE","ONEDRIVE"]:
#                 if bOpen: #if there is a change in file


#                     print("")
#                 else:
#                     compressed_data = SENTINEL_NO_CHANGE #b"{44A0C353-B685-4F9E-A3CF-08050440A814}

#             chunk_num = 0
#             seq_num = 0
#             t_c_count =num_chunks
#             i=0
#             futures = []
#             with open(open_file_name, "rb") as f:# , ThreadPoolExecutor(max_workers=8) as executor:
#             #with open(open_file_name, "rb") as f:
#                 chunk_data = f.read(chunk_size) if bOpen else b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
#                 while chunk_data:
#                     i=i+1
#                     t_c_count=t_c_count-1
#                     chunk = BytesIO()
                    
#                     with py7zr.SevenZipFile(chunk, 'w', password=s_7z_iv, 
#                                             filters=[{"id": py7zr.FILTER_ZSTD},
#                                                      {"id": py7zr.FILTER_CRYPTO_AES256_SHA256, "password": s_7z_iv}]) as archive:
#                         archive.writestr(data=chunk_data, arcname=f"chunk_{i}.abzv2")
                    
#                     chunk_data = f.read(chunk_size) if bOpen else None
#                     password = time.time()
#                     if bOpen :
#                         compressed_chunk = gzip.compress(chunk.getvalue(), 1, mtime=password)
#                     else:
#                         compressed_chunk = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"

#                     root_ = root
#                     seq_num = seq_num + 1
#                     if repo in ["LAN", "LOCAL", "LOCAL STORAGE"]:

#                         print("")
#                     elif str(repo).upper() in ["GDRIVE","AWSS3","AZURE","ONEDRIVE"]:
#                         print("")

#                     headers = {
#                         "File-Name": file,
#                         "fidi": digest,
#                         "tfi": tfi, #str(uuid.uuid4())
#                         "quNu": str(seq_num),
#                         "tc": str(num_chunks ),#str(math.ceil(len(compressed_data) / chunk_size)), #str(t_c),
#                         "abt": "False",
#                         "givn": base64.b64encode(gzip.compress(s_7z_iv.encode("UTF-8"), 9, mtime=password)),
#                         "epc": base64.b64encode(
#                             gzip.compress(
#                                 str(str(app.config.get("getCode",None))).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "epn": base64.b64encode(
#                             gzip.compress(
#                                 str(str(app.config.get("getCodea",None))).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "tcc": base64.b64encode(
#                             gzip.compress(
#                                 os.path.join(
#                                     str(str(app.config.get("getCode",None))), str(root).replace(":", "{{DRIVE}}")
#                                 ).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "tccsrc": base64.b64encode(
#                             gzip.compress(
#                                 os.path.join(
#                                     str(str(app.config.get("getCode",None))), str(src_location).replace(":", "{{DRIVE}}")
#                                 ).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         # , trg_folder, p_name, repo, authId
#                         "tf": base64.b64encode(
#                             gzip.compress(
#                                 str(trg_folder).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "pna": base64.b64encode(
#                             gzip.compress(
#                                 str(p_name).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "rep": base64.b64encode(
#                             gzip.compress(
#                                 str(repo).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "ahi": base64.b64encode(
#                             gzip.compress(
#                                 str(authId).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "jsta": base64.b64encode(
#                             gzip.compress(
#                                 str(job_Start).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "mimet": base64.b64encode(
#                             gzip.compress(
#                                 str(ftype).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "pNameText": base64.b64encode(
#                             gzip.compress(
#                                 str(p_NameText).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "pIdText": base64.b64encode(
#                             gzip.compress(
#                                 str(p_IdText).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "bkupType": base64.b64encode(
#                             gzip.compress(
#                                 str(bkupType).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "currentfile": base64.b64encode(
#                             gzip.compress(
#                                 str(currentfile).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                         "totalfiles": base64.b64encode(
#                             gzip.compress(
#                                 str(totalfiles).encode("UTF-8"),
#                                 9,
#                                 mtime=password,
#                             )
#                         ),
#                     }

#                     try:
#                         response=None
#                         if bOpen :
#                             files = {'file': (f'chunk_{file}_{seq_num}.bin', compressed_chunk, 'application/octet-stream')}
#                         else: 
#                             files = compressed_chunk
#                         del compressed_chunk
#                         from requests_file import FileAdapter
#                         for attempt in RETRY_LIMIT:
                            
#                             try:
#                                 if bOpen :
#                                     response = requests.post(url, files=files, headers=headers)#, timeout=(30000,30000))
#                                     response.raise_for_status()
#                                     break
#                                 else:
#                                     response = requests.post(url,  data=files, headers=headers)#, timeout=(30000,30000))
#                                     response.raise_for_status()
#                                     break
#                             except Exception as e:
#                                 backoff = RETRY_BACKOFF_BASE ** attempt
#                                 print(f"Retrying to connect to server...........{backoff}")
#                                 time.sleep(backoff)


#                         if response.status_code == 200:
#                             print(
#                                 f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
#                             )
#                             if (
#                                 str((response.json())["result"]["status"]).lower()
#                                 == "failed"
#                             ):
#                                 raise RuntimeError(
#                                     str((response.json())["result"]["status"])
#                                 )
#                                 break
#                         else:
#                             print(
#                                 f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
#                             )
#                             if (
#                                 str((response.json())["result"]["status"]).lower()
#                                 == "failed"
#                             ):
#                                 raise RuntimeError(
#                                     str((response.json())["result"]["status"])
#                                 )
#                                 break

#                     except Exception as ser:
#                         print(str(ser))
#                         raise RuntimeError(str(ser))

#         else:
#             if cl_socketio_obj.connected:
#                 cl_socketio_obj.disconnect()
#             print("11data not found in file")
#             #raise RuntimeError(str("11data not found in file")) 
#     except Exception as sere:

#         if cl_socketio_obj.connected:
#             cl_socketio_obj.disconnect()
#         print(str(sere))
#         raise RuntimeError(str(sere)) 

#     if cl_socketio_obj.connected:
#         cl_socketio_obj.disconnect()
