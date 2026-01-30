
    #     with Open(file_name, "rb") as m_file:
    #         with mmap.mmap(m_file.fileno(), 0, access=mmap.ACCESS_COPY) as f:
    #             cdigest=FileDig()
    #             digest= cdigest._hash_memory(f)
    #             file_size = m_file.seek(0, 2) 
    #             m_file.seek(0)
    #             del cdigest
    #             f.seek(0)
    #             if bOpen:
    #                 compression_level= 1

    #                 f.seek(0)
    #                 #compressed_data = f.read()
    #                 shm= multiprocessing.shared_memory.SharedMemory(create=True,size=file_size)
    #                 shm.buf[:file_size] = f[:]
    #                 chunk_size = get_optimal_chunk_size(file_size=file_size)
    #                 num_chunks=file_size//chunk_size
    #                 compressed_data =num_chunks !=0
    #                 t_c = math.ceil(file_size / chunk_size)
    #             f.close()
    #             if not bOpen:
    #                 compressed_data = b""
    #             if compressed_data:
    #                 if repo in ["dsfad"]:
    #                     if bOpen: #if there is a change in file
    #                         #compressed_data = zlib.compress(compressed_data,level=int(compression_level))
    #                         pZip= p7zstd(iv,preset=int(compression_level))
    #                         compressed_data = pZip.compress_chunk_shared(shm_name= shm.name,chunk_size= chunk_size,num_chunks= num_chunks)
    #                         #compressed_data= pZip.compress(data=compressed_data,file_name=file_name)
    #                         del pZip
    #                         shm.unlink()
    #                         shm.close()

    #                         print("")
    #                     else:
    #                         compressed_data = b""
    #                     if isinstance(iv,(str)):
    #                         #iv = bytes.fromhex(iv)
    #                         iv = iv.encode()

    #                 chunk_num = 0
    #                 seq_num = 0

            
    #                 t_c_count = math.ceil(len(compressed_data) / chunk_size)+1
    #                 for i in range(0, len(compressed_data), chunk_size):
    #                     t_c_count=t_c_count-1
    #                     chunk = compressed_data[i : i + chunk_size]
    #                     isLast = (i + chunk_size) ==len(compressed_data)
    #                     if isLast or t_c_count==1:
    #                         print("ppppppppppppppppppppppppppppppppppppppppppppppppppppppp")
    #                     # chunk = f.read(chunk_size)
    #                     # seq_num = 0
    #                     # while chunk:

    #                     password = time.time()
    #                     compressed_chunk = gzip.compress(chunk, 1, mtime=password)

    #                     root_ = root
    #                     seq_num = seq_num + 1
    #                     if repo in ["dsfad"]:
    #                         compressed_chunk = gzip.compress(chunk, 1, mtime=password)
    #                         print("")
    #                     elif str(repo).upper() in ["GDRIVE","AWSS3","AZURE"]:
    #                         # compressed_chunk = gzip.compress(
    #                         #     compressed_chunk, 9, mtime=password
    #                         # )
    #                         compressed_chunk = gzip.compress(
    #                             chunk, 9, mtime=password
    #                         )

    #                     headers = {
    #                         "File-Name": file,
    #                         "fidi": digest,
    #                         "quNu": str(seq_num),
    #                         "tc": str(math.ceil(len(compressed_data) / chunk_size)), #str(t_c),
    #                         "abt": "False",
    #                         "givn": base64.b64encode(
    #                             gzip.compress(
    #                                 str(iv.hex()).encode("UTF-8"),
    #                                 9,
    #                                 mtime=password,
    #                             )
    #                         ),
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
 
    #                         files = {'file': (f'chunk_{file}_{seq_num}.bin', compressed_chunk, 'application/octet-stream')}
    #                         from requests_file import FileAdapter
                            
    #                         response = requests.post(
    #                             url, files=files, headers=headers, timeout=(3000,3000)
    #                         )
    #                         del compressed_chunk
    #                         # chunk = f.read(chunk_size)

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
    #             else:

    #                 raise RuntimeError(str("data not found in file")) 
 

    
    # if shm:
    #     shm.unlink()
    #     shm.close()
    # if cl_socketio_obj.connected:
    #     cl_socketio_obj.disconnect

