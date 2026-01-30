    # def decompress(self, encrypted_data: bytes, file_name: str) -> bytes:
    #     """
    #     Decrypt and decompress data using py7zr.

    #     :param encrypted_data: Encrypted and compressed bytes
    #     :param file_name: The name of the file expected within the archive
    #     :return: Original decompressed bytes
    #     """
    #     encrypted_stream = io.BytesIO(encrypted_data)
    #     expected_name = os.path.basename(file_name)
    #     try:
    #         with py7zr.SevenZipFile(encrypted_stream, 'r', password=self.password) as archive:
    #             extracted = archive.readall()  # Read all files
                
    #             data=io.BytesIO()
    #             if extracted:
    #                 for edata in extracted:# archive.readall().items: #extracted:
    #                     data.write(extracted[edata].getvalue())
    #                     print(len(data.getvalue()))
    #                 return data.getvalue()
    #             # if expected_name in extracted:
    #             #     return extracted[expected_name].getvalue()
    #             else:
    #                 raise ValueError(f"File '{expected_name}' not found in the archive.")
    #     except py7zr.exceptions.PasswordRequired:
    #         raise ValueError("Incorrect password for the 7z archive.")
    #     except py7zr.exceptions.Bad7zFile as sef :
    #         raise ValueError("The provided data is not a valid 7z archive.")
    #     except Exception as e:
    #         raise Exception(f"Decompression error: {e}")
