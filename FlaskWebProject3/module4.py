# import builtins
# from fileinput import filename
# # from os import *
# import os
# from os.path import join, getsize
# import time
# import platform
# import subprocess
# import ctypes
# import json
# import stat

# # t1 = time.time()
# # size = 9999999999999999999
# # size2 = 9999999999999999999
# # print(time.time())
# # size2 = sum(
# #     sum(os.path.getsize(os.path.join(dirpath, filename)) for filename in filenames)
# #     for dirpath, _, filenames in os.walk("C:\Program Files")
# # )
# # # size2 = sum(sum(os.path.getsize(os.path.join(dirpath, filename)) for filename in filenames) for dirpath, _, filenames in os.walk("C:\Program Files"))
# # # size3 = [ {'path':dirpath, 'files':  [{ 'fileMode': stat.filemode(os.stat( path.join(dirpath, g)).st_mode), 'creationTime': time.ctime(os.stat( path.join(dirpath, g)).st_ctime),'lastAccessed': time.ctime(os.stat( path.join(dirpath, g)).st_atime), 'lastModified': time.ctime(os.stat( path.join(dirpath, g)).st_mtime), 'file': path.join(dirpath, g), 'size': os.path.getsize(os.path.join(dirpath, g))}   for g in filenames ]}   for dirpath, _, filenames in os.walk("C:\jjj_546")]
# # size3 = ["size": sum(            sum(                os.path.getsize(os.path.join(dirpath, filename))
# #                 for filename in filenames
# #             )
# #             for g in filenames
# #         ),
# #     "Data":{
        
# #         "path": dirpath,
# #         "files": [
# #             {
# #                 "fileMode": stat.filemode(os.stat(path.join(dirpath, g)).st_mode),
# #                 "creationTime": os.stat(path.join(dirpath, g)).st_ctime,
# #                 "lastAccessed": time.ctime(os.stat(path.join(dirpath, g)).st_atime),
# #                 "lastModified": time.ctime(os.stat(path.join(dirpath, g)).st_mtime),
# #                 "file": path.join(dirpath, g),
# #                 "size": os.path.getsize(os.path.join(dirpath, g)),
# #             }
# #             for g in filenames
# #         ],
# #     }
# #     for dirpath, _, filenames in os.walk("C:\\Documents and Settings")
# # ]
# # t2 = time.time()
# # size = 0
# # a = walk("D:\Server20032020_1751")
# # a = walk("C:\\")
# # for x, y, z in a:
# #     print(x, "consumes", end=" +++++++++++++ ")
# #     size = size + sum(getsize(join(x, name)) for name in z)
# #     print(getsize(join(x, y[0])))
# #     print(size)
# #     # print("bytes in 9(", len(z), ") non-directory files")

# # os.system("cls")
# # os.system("echo Hello, World!")
# # subprocess.run(["cls"], shell=False)
# # # print("\033[H\033[J", end="")
# # # ctypes.windll.kernel32.SetConsoleTextAttribute(ctypes.windll.kernel32.GetStdHandle(-11), 0)

# # t3 = time.time()
# # print(
# #     f"{t2-t1} , {t3-t2}, {size}, {size//1024//1024}, {size2//1000//1000}, {size}, {size2//1024//1024}, {size2//1000//1000}"
# # )
# # print("")
# # print(json.dumps(size3))


# # data = b'{  "awaited": {},  "pairedAgents": {    "4d6a457a4e574933-597a646959544930-4d6a51305a6a6b78-5a6d4d304e7a5177-5a6a51304d7a6b34-4d6d4d774f444a6d-4e4451795a6a5578-4e3255344e6a4131-5a6a557a4d324531-4d4463325a475532-4d6d4a694d773d3d": {      "IPname": "ADMIN",      "activationDate": "1763715429.990839",      "activationkey": "4d6a457a4e574933-597a646959544930-4d6a51305a6a6b78-5a6d4d304e7a5177-5a6a51304d7a6b34-4d6d4d774f444a6d-4e4451795a6a5578-4e3255344e6a4131-5a6a557a4d324531-4d4463325a475532-4d6d4a694d773d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "BHlbBr62yyWcj0B7rzXInq8v23tB7w672WRKdNkxtp505uk7X2K0cjCnsjmrPWe4F5UjwANEtaaqcg9x3VhQDNXTEJDrIO5erScnBCDcmojFZjtHuEiOV4wDx4j8H5Uk",      "status": "Active"    },    "4d6d457a5a546332-4e6a59354e544e6c-4d474e6d4e54557a-4e6d517a4d444a6c-5a6a426b596a5931-4f544d78596a5930-4f5463354f545133-4e6a4a684d545132-4d7a67355a57466d-4e6a4669596a5131-5a54466b4d413d3d": {      "IPname": "JAISINGH",      "activationDate": "1763715449.86605",      "activationkey": "4d6d457a5a546332-4e6a59354e544e6c-4d474e6d4e54557a-4e6d517a4d444a6c-5a6a426b596a5931-4f544d78596a5930-4f5463354f545133-4e6a4a684d545132-4d7a67355a57466d-4e6a4669596a5131-5a54466b4d413d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "my0AVXFjDFApPXdOG3OzyhpKZD8IiJSqMZo0HnotGe75sCxIau067qPEUes3dgiiEnNV1RbzPh8xupKf65xjEJljHnEKd38alMBbfjmDHvVQ0DBaZGdobdLBHLuLjjUt",      "status": "Active"    },    "4e324d3259575668-4d6d49324d544133-4e54493359325a6b-5a444a6859325a6b-5a6d466b59544531-5a44466a597a6c6a-4d7a51344e6a526a-596a64694d54466d-4d5449305a6d4a68-4d6a686d4e47466a-4f4449784e513d3d": {      "IPname": "Geetika",      "activationDate": "1758719543.50084",      "activationkey": "4e324d3259575668-4d6d49324d544133-4e54493359325a6b-5a444a6859325a6b-5a6d466b59544531-5a44466a597a6c6a-4d7a51344e6a526a-596a64694d54466d-4d5449305a6d4a68-4d6a686d4e47466a-4f4449784e513d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "lnPrgTMAbzpt0mN1ctrWa2BrPKSKOi43pcST9Q4tq36IZ5aD8mLPLRGz90gc3E6bqsv2lS1PB2P0QuAQ1jWVar4Y4G87G1PwCLgw8aRQcHJLsx1mSTe35WD5WHV78zPw",      "status": "Active"    },    "4e54677a4e6d4a6a-4e54677a4f445133-4e3255354e7a5931-4e544a694d57497a-4e3251794e6a5a69-4e4751314e7a4979-4e6a4e694d7a686a-4e4463774e6a5668-4d3246695a575931-4d4441354d474a69-4e3259325a673d3d": {      "IPname": "ONLY-DATA",      "activationDate": "1763715440.809538",      "activationkey": "4e54677a4e6d4a6a-4e54677a4f445133-4e3255354e7a5931-4e544a694d57497a-4e3251794e6a5a69-4e4751314e7a4979-4e6a4e694d7a686a-4e4463774e6a5668-4d3246695a575931-4d4441354d474a69-4e3259325a673d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "XNoHPwbjqHTUaG9e9jZzBvur0VEFiCWwyXWR8tfE1Jfniy01aLwn68fIks9uax8T7k1QqgECiZYA0LdCIiUPXTdR0AAsNYvCjJiuvBZQIoWjSzDGsa081Ai0R6g2NVFp",      "status": "Active"    },    "4e6a5268597a6377-5a6a566c4e544131-4e446c6c4e7a6869-4e545535596a5a6b-4d444a6d4d7a4a6a-5a5751334d57497a-4f474a6a5a544e6d-595467774d445532-4d54426c4f444a6c-596a597a59544930-593256694d673d3d": {      "IPname": "KPSERVERNEW",      "activationDate": "1758632008.011659",      "activationkey": "4e6a5268597a6377-5a6a566c4e544131-4e446c6c4e7a6869-4e545535596a5a6b-4d444a6d4d7a4a6a-5a5751334d57497a-4f474a6a5a544e6d-595467774d445532-4d54426c4f444a6c-596a597a59544930-593256694d673d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "Vy5kOencI75LHLxlD1X9DutIqSxAnrjBRxVgiN8hD7sWZU9agsgbKaZEknvhEDFxqUdLUsa482XQbk0PA9c8oqCuxxdAugCo9JN57NrzNqFqnmyr1ZNATrGDWd2IwUJw",      "status": "Active"    },    "4f54526959324979-59544a684d7a4934-4d5759304e475a6d-4d544e684e575935-4e6d5931596d466b-59574d305a6a6377-5a5445774d544133-4d4441795a444d34-4d324a6d4f444132-4d574d324e44566c-597a566959673d3d": {      "IPname": "shekhar",      "activationDate": "1758719551.621939",      "activationkey": "4f54526959324979-59544a684d7a4934-4d5759304e475a6d-4d544e684e575935-4e6d5931596d466b-59574d305a6a6377-5a5445774d544133-4d4441795a444d34-4d324a6d4f444132-4d574d324e44566c-597a566959673d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "IrxXg8icFi8Ph12Yh4DI6GYlCVJGiQYu69oBCuvKItBcvBXTPpOqo8dknK5gFNuwkYDgagDdfy2tMMLVVp3ZhlnfZr94tKBHaK5QNH6rVSrOSVJ9YA13phkZN1Fjc7tF",      "status": "Active"    },    "59324a68596d5532-5a6a686a59546c6a-5954526c4e6a4135-4f5449314d54677a-596d466a597a5530-5a6a67314e325a6b-4d54517859546778-595445354f545532-5a4449774e6a4d35-4d6d49355a47466c-59546b7a59773d3d": {      "IPname": "DESKTOP-0F5MI6P",      "activationDate": "1758719558.314632",      "activationkey": "59324a68596d5532-5a6a686a59546c6a-5954526c4e6a4135-4f5449314d54677a-596d466a597a5530-5a6a67314e325a6b-4d54517859546778-595445354f545532-5a4449774e6a4d35-4d6d49355a47466c-59546b7a59773d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "7rb8inDC8jk1v3j1xFQ1XHpr5qhTQhF4hV3hil07LmfrShLV0T1rmvClhxYjq4mkeISSYWH6gr7LVZa8SkXW6p32Z09oMfbYpNcYQC58vJSPp7bijX9ENCnYQ51aG6Wd",      "status": "Active"    },    "5957466b59574978-5a5456695a6a6332-4e6a52684d6d4533-4f546b304d574934-4d446b324e7a5133-5a5745315a54566c-4e6d51795954526c-5a4759335a6a426d-4e544130596a646b-596d5a6d5a546b30-4f446c6c4d413d3d": {      "IPname": "KPSERVERNEW",      "activationDate": "1765957057.968206",      "activationkey": "5957466b59574978-5a5456695a6a6332-4e6a52684d6d4533-4f546b304d574934-4d446b324e7a5133-5a5745315a54566c-4e6d51795954526c-5a4759335a6a426d-4e544130596a646b-596d5a6d5a546b30-4f446c6c4d413d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "0VNFZcNtXwmQIMM7uW5cc6OhMo9LCndyJXpeyEcKqDWOcjPMgXpVlC05xM9vvOpSRYT0coNO3gmVMwItt7FlnZU8UoZtxT6aD5q6DsupFkM9myGwkcd28l1pSuYk4Hxx",      "status": "Active"    },    "596a56695a575130-4d6a42685a545932-596a4578597a6733-4e6a49304e444535-5a4463345a474d31-4f47466b4e7a6c6c-596a67785a575a69-5a47517a4e54646c-4e7a566c4d57517a-4e446b354d544d34-596a56694f413d3d": {      "IPname": "DESKTOP-SBBN93C",      "activationDate": "1763715457.226218",      "activationkey": "596a56695a575130-4d6a42685a545932-596a4578597a6733-4e6a49304e444535-5a4463345a474d31-4f47466b4e7a6c6c-596a67785a575a69-5a47517a4e54646c-4e7a566c4d57517a-4e446b354d544d34-596a56694f413d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "vuNPerj4sc1utoGbuwaXxX2vCRMkssdIUzI3ICRLOUrKc7x21mKkTKUZbJQvHxvUSYXIY2M1Hax0iWIgGMG2CjnuFWzieDuENtJwa4PDx3Ak4x9IRHB1ClJpGMbiECkN",      "status": "Active"    },    "5a6a5933597a5135-4d4759334d545531-4d6a4a6c4e7a5668-4d6a55794d475668-4f546332597a4178-4d3252695a544d31-597a686c4d7a4977-4e7a51344e575131-5a6a4e6b4e7a6731-4e6a557a596a4a69-4d7a4d314f413d3d": {      "IPname": "DESKTOP-94G82QL",      "activationDate": "1758719566.351687",      "activationkey": "5a6a5933597a5135-4d4759334d545531-4d6a4a6c4e7a5668-4d6a55794d475668-4f546332597a4178-4d3252695a544d31-597a686c4d7a4977-4e7a51344e575131-5a6a4e6b4e7a6731-4e6a557a596a4a69-4d7a4d314f413d3d",      "application": "Apna-Backup-Endpoint",      "licensekey": "lFdN4A14eYWQdhhZ2x5zW10ZXCm3pxAoBHyUmYc4hgcIZYJmkoG4QRjJYjsXkTYw0yIkBmmRAPLtYmIZ8KQa2qtdU5eOGZlj90wqSacrJpxYD1h37U9PJC4xdD9QJRWt",      "status": "Active"    }  },  "unpairedAgents": {}}'
# # data = data.decode()
# data = "{'server': {'IPname': 'AB-SRV', 'activationkey': '4e4451795a44417a-596d5a6d5a6a566d-4d6a4e684d574a69-4d4445304e546b32-4e5452684e6d4934-4d574e6b4f57526c-4f544d794e446b32-5a6a6c694d32526d-5a5745324e6d466a-4d446c6d4f574d30-4e6d4e6b4d513d3d', 'licensekey': 'gFTCchyBcDlTGld21kWZOtyFoDrkzQITKFMhNcVyyISCVbKyqiGDrk065RUOQUUuxTzOCh5f317auswfUTcaOpHIRLYqm1Mb0Ish9e1M86Mrnok1IaS8HR8FYkEY5KC8', 'activationDate': '1766044139.0', 'status': 'Active', 'application': 'Apna-Backup-Server'}, 'Endpoints': [{'IPname': 'KPSERVERNEW', 'activationkey': '4e6a5268597a6377-5a6a566c4e544131-4e446c6c4e7a6869-4e545535596a5a6b-4d444a6d4d7a4a6a-5a5751334d57497a-4f474a6a5a544e6d-595467774d445532-4d54426c4f444a6c-596a597a59544930-593256694d673d3d', 'licensekey': 'Vy5kOencI75LHLxlD1X9DutIqSxAnrjBRxVgiN8hD7sWZU9agsgbKaZEknvhEDFxqUdLUsa482XQbk0PA9c8oqCuxxdAugCo9JN57NrzNqFqnmyr1ZNATrGDWd2IwUJw', 'activationDate': '1758632008.011659', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'Geetika', 'activationkey': '4e324d3259575668-4d6d49324d544133-4e54493359325a6b-5a444a6859325a6b-5a6d466b59544531-5a44466a597a6c6a-4d7a51344e6a526a-596a64694d54466d-4d5449305a6d4a68-4d6a686d4e47466a-4f4449784e513d3d', 'licensekey': 'lnPrgTMAbzpt0mN1ctrWa2BrPKSKOi43pcST9Q4tq36IZ5aD8mLPLRGz90gc3E6bqsv2lS1PB2P0QuAQ1jWVar4Y4G87G1PwCLgw8aRQcHJLsx1mSTe35WD5WHV78zPw', 'activationDate': '1758719543.50084', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'KPSERVERNEW', 'activationkey': '5957466b59574978-5a5456695a6a6332-4e6a52684d6d4533-4f546b304d574934-4d446b324e7a5133-5a5745315a54566c-4e6d51795954526c-5a4759335a6a426d-4e544130596a646b-596d5a6d5a546b30-4f446c6c4d413d3d', 'licensekey': '0VNFZcNtXwmQIMM7uW5cc6OhMo9LCndyJXpeyEcKqDWOcjPMgXpVlC05xM9vvOpSRYT0coNO3gmVMwItt7FlnZU8UoZtxT6aD5q6DsupFkM9myGwkcd28l1pSuYk4Hxx', 'activationDate': '1765957057.968206', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'shekhar', 'activationkey': '4f54526959324979-59544a684d7a4934-4d5759304e475a6d-4d544e684e575935-4e6d5931596d466b-59574d305a6a6377-5a5445774d544133-4d4441795a444d34-4d324a6d4f444132-4d574d324e44566c-597a566959673d3d', 'licensekey': 'IrxXg8icFi8Ph12Yh4DI6GYlCVJGiQYu69oBCuvKItBcvBXTPpOqo8dknK5gFNuwkYDgagDdfy2tMMLVVp3ZhlnfZr94tKBHaK5QNH6rVSrOSVJ9YA13phkZN1Fjc7tF', 'activationDate': '1758719551.621939', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'DESKTOP-0F5MI6P', 'activationkey': '59324a68596d5532-5a6a686a59546c6a-5954526c4e6a4135-4f5449314d54677a-596d466a597a5530-5a6a67314e325a6b-4d54517859546778-595445354f545532-5a4449774e6a4d35-4d6d49355a47466c-59546b7a59773d3d', 'licensekey': '7rb8inDC8jk1v3j1xFQ1XHpr5qhTQhF4hV3hil07LmfrShLV0T1rmvClhxYjq4mkeISSYWH6gr7LVZa8SkXW6p32Z09oMfbYpNcYQC58vJSPp7bijX9ENCnYQ51aG6Wd', 'activationDate': '1758719558.314632', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'DESKTOP-94G82QL', 'activationkey': '5a6a5933597a5135-4d4759334d545531-4d6a4a6c4e7a5668-4d6a55794d475668-4f546332597a4178-4d3252695a544d31-597a686c4d7a4977-4e7a51344e575131-5a6a4e6b4e7a6731-4e6a557a596a4a69-4d7a4d314f413d3d', 'licensekey': 'lFdN4A14eYWQdhhZ2x5zW10ZXCm3pxAoBHyUmYc4hgcIZYJmkoG4QRjJYjsXkTYw0yIkBmmRAPLtYmIZ8KQa2qtdU5eOGZlj90wqSacrJpxYD1h37U9PJC4xdD9QJRWt', 'activationDate': '1758719566.351687', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'ADMIN', 'activationkey': '4d6a457a4e574933-597a646959544930-4d6a51305a6a6b78-5a6d4d304e7a5177-5a6a51304d7a6b34-4d6d4d774f444a6d-4e4451795a6a5578-4e3255344e6a4131-5a6a557a4d324531-4d4463325a475532-4d6d4a694d773d3d', 'licensekey': 'BHlbBr62yyWcj0B7rzXInq8v23tB7w672WRKdNkxtp505uk7X2K0cjCnsjmrPWe4F5UjwANEtaaqcg9x3VhQDNXTEJDrIO5erScnBCDcmojFZjtHuEiOV4wDx4j8H5Uk', 'activationDate': '1763715429.990839', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'ONLY-DATA', 'activationkey': '4e54677a4e6d4a6a-4e54677a4f445133-4e3255354e7a5931-4e544a694d57497a-4e3251794e6a5a69-4e4751314e7a4979-4e6a4e694d7a686a-4e4463774e6a5668-4d3246695a575931-4d4441354d474a69-4e3259325a673d3d', 'licensekey': 'XNoHPwbjqHTUaG9e9jZzBvur0VEFiCWwyXWR8tfE1Jfniy01aLwn68fIks9uax8T7k1QqgECiZYA0LdCIiUPXTdR0AAsNYvCjJiuvBZQIoWjSzDGsa081Ai0R6g2NVFp', 'activationDate': '1763715440.809538', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'JAISINGH', 'activationkey': '4d6d457a5a546332-4e6a59354e544e6c-4d474e6d4e54557a-4e6d517a4d444a6c-5a6a426b596a5931-4f544d78596a5930-4f5463354f545133-4e6a4a684d545132-4d7a67355a57466d-4e6a4669596a5131-5a54466b4d413d3d', 'licensekey': 'my0AVXFjDFApPXdOG3OzyhpKZD8IiJSqMZo0HnotGe75sCxIau067qPEUes3dgiiEnNV1RbzPh8xupKf65xjEJljHnEKd38alMBbfjmDHvVQ0DBaZGdobdLBHLuLjjUt', 'activationDate': '1763715449.86605', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'DESKTOP-SBBN93C', 'activationkey': '596a56695a575130-4d6a42685a545932-596a4578597a6733-4e6a49304e444535-5a4463345a474d31-4f47466b4e7a6c6c-596a67785a575a69-5a47517a4e54646c-4e7a566c4d57517a-4e446b354d544d34-596a56694f413d3d', 'licensekey': 'vuNPerj4sc1utoGbuwaXxX2vCRMkssdIUzI3ICRLOUrKc7x21mKkTKUZbJQvHxvUSYXIY2M1Hax0iWIgGMG2CjnuFWzieDuENtJwa4PDx3Ak4x9IRHB1ClJpGMbiECkN', 'activationDate': '1763715457.226218', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}], 'Revoked_Endpoints': [{'IPname': 'DESKTOP-7GFHN2K', 'activationkey': '5a54646c4d544a6c-4d5441304d574d31-5a575a6c5a545578-4d47566c5a6a5177-4d5751354f546b32-5a54566859546330-4d7a426859325933-4e6d4d7a5a6a6778-4d6a49774e7a6335-4f5751784d444935-4d32466d5a673d3d', 'licensekey': 'y5knr9YdPHgvmn92qCrGchbJlXixrcRTITJu9aTgEzhznYqZjZnLt13604Itt3vOcOWA6gZhOAT2cQEwJ6wo4Ezwul0XBpKnEgNNt3LwS4lYz7Nw1GmLdcffo462v5NX', 'activationDate': '1748068916.898', 'status': 'deactivate', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'Accounts-admin', 'activationkey': '4f5445774e546b78-4d6a4e6c4f574578-4e7a4534597a466a-4d5445305a444d35-595752685a54686c-4d6a42684f545979-5a57566b4d54426d-596a4d79597a5178-4e6a67354e324d77-595446694e6a6777-4e4459795a413d3d', 'licensekey': 'W12PgN03pIPpRqBYp5apMEpCmR1HVGQol0ByG0oktnaUmbLcAjSYq1dmEt4vHadWAPPuYf864RrXyrZn3s9m3E5Mv9wYlVTrUXQHKjcpvxxYLWeOaNRrloyIodIydtc9', 'activationDate': '1748070228.164', 'status': 'deactivate', 'application': 'Apna-Backup-Endpoint'}], 'awaited_Endpoints': [], 'last_updated': '1766754331.996222'}"
# data ="{'server': {'IPname': 'AB-SRV', 'activationkey': '4e4451795a44417a-596d5a6d5a6a566d-4d6a4e684d574a69-4d4445304e546b32-4e5452684e6d4934-4d574e6b4f57526c-4f544d794e446b32-5a6a6c694d32526d-5a5745324e6d466a-4d446c6d4f574d30-4e6d4e6b4d513d3d', 'licensekey': 'gFTCchyBcDlTGld21kWZOtyFoDrkzQITKFMhNcVyyISCVbKyqiGDrk065RUOQUUuxTzOCh5f317auswfUTcaOpHIRLYqm1Mb0Ish9e1M86Mrnok1IaS8HR8FYkEY5KC8', 'activationDate': '1766044139.0', 'status': 'Active', 'application': 'Apna-Backup-Server'}, 'Endpoints': [{'IPname': 'KPSERVERNEW', 'activationkey': '4e6a5268597a6377-5a6a566c4e544131-4e446c6c4e7a6869-4e545535596a5a6b-4d444a6d4d7a4a6a-5a5751334d57497a-4f474a6a5a544e6d-595467774d445532-4d54426c4f444a6c-596a597a59544930-593256694d673d3d', 'licensekey': 'Vy5kOencI75LHLxlD1X9DutIqSxAnrjBRxVgiN8hD7sWZU9agsgbKaZEknvhEDFxqUdLUsa482XQbk0PA9c8oqCuxxdAugCo9JN57NrzNqFqnmyr1ZNATrGDWd2IwUJw', 'activationDate': '1758632008.011659', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'Geetika', 'activationkey': '4e324d3259575668-4d6d49324d544133-4e54493359325a6b-5a444a6859325a6b-5a6d466b59544531-5a44466a597a6c6a-4d7a51344e6a526a-596a64694d54466d-4d5449305a6d4a68-4d6a686d4e47466a-4f4449784e513d3d', 'licensekey': 'lnPrgTMAbzpt0mN1ctrWa2BrPKSKOi43pcST9Q4tq36IZ5aD8mLPLRGz90gc3E6bqsv2lS1PB2P0QuAQ1jWVar4Y4G87G1PwCLgw8aRQcHJLsx1mSTe35WD5WHV78zPw', 'activationDate': '1758719543.50084', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'KPSERVERNEW', 'activationkey': '5957466b59574978-5a5456695a6a6332-4e6a52684d6d4533-4f546b304d574934-4d446b324e7a5133-5a5745315a54566c-4e6d51795954526c-5a4759335a6a426d-4e544130596a646b-596d5a6d5a546b30-4f446c6c4d413d3d', 'licensekey': '0VNFZcNtXwmQIMM7uW5cc6OhMo9LCndyJXpeyEcKqDWOcjPMgXpVlC05xM9vvOpSRYT0coNO3gmVMwItt7FlnZU8UoZtxT6aD5q6DsupFkM9myGwkcd28l1pSuYk4Hxx', 'activationDate': '1765957057.968206', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'shekhar', 'activationkey': '4f54526959324979-59544a684d7a4934-4d5759304e475a6d-4d544e684e575935-4e6d5931596d466b-59574d305a6a6377-5a5445774d544133-4d4441795a444d34-4d324a6d4f444132-4d574d324e44566c-597a566959673d3d', 'licensekey': 'IrxXg8icFi8Ph12Yh4DI6GYlCVJGiQYu69oBCuvKItBcvBXTPpOqo8dknK5gFNuwkYDgagDdfy2tMMLVVp3ZhlnfZr94tKBHaK5QNH6rVSrOSVJ9YA13phkZN1Fjc7tF', 'activationDate': '1758719551.621939', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'DESKTOP-0F5MI6P', 'activationkey': '59324a68596d5532-5a6a686a59546c6a-5954526c4e6a4135-4f5449314d54677a-596d466a597a5530-5a6a67314e325a6b-4d54517859546778-595445354f545532-5a4449774e6a4d35-4d6d49355a47466c-59546b7a59773d3d', 'licensekey': '7rb8inDC8jk1v3j1xFQ1XHpr5qhTQhF4hV3hil07LmfrShLV0T1rmvClhxYjq4mkeISSYWH6gr7LVZa8SkXW6p32Z09oMfbYpNcYQC58vJSPp7bijX9ENCnYQ51aG6Wd', 'activationDate': '1758719558.314632', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'DESKTOP-94G82QL', 'activationkey': '5a6a5933597a5135-4d4759334d545531-4d6a4a6c4e7a5668-4d6a55794d475668-4f546332597a4178-4d3252695a544d31-597a686c4d7a4977-4e7a51344e575131-5a6a4e6b4e7a6731-4e6a557a596a4a69-4d7a4d314f413d3d', 'licensekey': 'lFdN4A14eYWQdhhZ2x5zW10ZXCm3pxAoBHyUmYc4hgcIZYJmkoG4QRjJYjsXkTYw0yIkBmmRAPLtYmIZ8KQa2qtdU5eOGZlj90wqSacrJpxYD1h37U9PJC4xdD9QJRWt', 'activationDate': '1758719566.351687', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'ADMIN', 'activationkey': '4d6a457a4e574933-597a646959544930-4d6a51305a6a6b78-5a6d4d304e7a5177-5a6a51304d7a6b34-4d6d4d774f444a6d-4e4451795a6a5578-4e3255344e6a4131-5a6a557a4d324531-4d4463325a475532-4d6d4a694d773d3d', 'licensekey': 'BHlbBr62yyWcj0B7rzXInq8v23tB7w672WRKdNkxtp505uk7X2K0cjCnsjmrPWe4F5UjwANEtaaqcg9x3VhQDNXTEJDrIO5erScnBCDcmojFZjtHuEiOV4wDx4j8H5Uk', 'activationDate': '1763715429.990839', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'ONLY-DATA', 'activationkey': '4e54677a4e6d4a6a-4e54677a4f445133-4e3255354e7a5931-4e544a694d57497a-4e3251794e6a5a69-4e4751314e7a4979-4e6a4e694d7a686a-4e4463774e6a5668-4d3246695a575931-4d4441354d474a69-4e3259325a673d3d', 'licensekey': 'XNoHPwbjqHTUaG9e9jZzBvur0VEFiCWwyXWR8tfE1Jfniy01aLwn68fIks9uax8T7k1QqgECiZYA0LdCIiUPXTdR0AAsNYvCjJiuvBZQIoWjSzDGsa081Ai0R6g2NVFp', 'activationDate': '1763715440.809538', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'JAISINGH', 'activationkey': '4d6d457a5a546332-4e6a59354e544e6c-4d474e6d4e54557a-4e6d517a4d444a6c-5a6a426b596a5931-4f544d78596a5930-4f5463354f545133-4e6a4a684d545132-4d7a67355a57466d-4e6a4669596a5131-5a54466b4d413d3d', 'licensekey': 'my0AVXFjDFApPXdOG3OzyhpKZD8IiJSqMZo0HnotGe75sCxIau067qPEUes3dgiiEnNV1RbzPh8xupKf65xjEJljHnEKd38alMBbfjmDHvVQ0DBaZGdobdLBHLuLjjUt', 'activationDate': '1763715449.86605', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'DESKTOP-SBBN93C', 'activationkey': '596a56695a575130-4d6a42685a545932-596a4578597a6733-4e6a49304e444535-5a4463345a474d31-4f47466b4e7a6c6c-596a67785a575a69-5a47517a4e54646c-4e7a566c4d57517a-4e446b354d544d34-596a56694f413d3d', 'licensekey': 'vuNPerj4sc1utoGbuwaXxX2vCRMkssdIUzI3ICRLOUrKc7x21mKkTKUZbJQvHxvUSYXIY2M1Hax0iWIgGMG2CjnuFWzieDuENtJwa4PDx3Ak4x9IRHB1ClJpGMbiECkN', 'activationDate': '1763715457.226218', 'status': 'Active', 'application': 'Apna-Backup-Endpoint'}], 'Revoked_Endpoints': [{'IPname': 'DESKTOP-7GFHN2K', 'activationkey': '5a54646c4d544a6c-4d5441304d574d31-5a575a6c5a545578-4d47566c5a6a5177-4d5751354f546b32-5a54566859546330-4d7a426859325933-4e6d4d7a5a6a6778-4d6a49774e7a6335-4f5751784d444935-4d32466d5a673d3d', 'licensekey': 'y5knr9YdPHgvmn92qCrGchbJlXixrcRTITJu9aTgEzhznYqZjZnLt13604Itt3vOcOWA6gZhOAT2cQEwJ6wo4Ezwul0XBpKnEgNNt3LwS4lYz7Nw1GmLdcffo462v5NX', 'activationDate': '1748068916.898', 'status': 'deactivate', 'application': 'Apna-Backup-Endpoint'}, {'IPname': 'Accounts-admin', 'activationkey': '4f5445774e546b78-4d6a4e6c4f574578-4e7a4534597a466a-4d5445305a444d35-595752685a54686c-4d6a42684f545979-5a57566b4d54426d-596a4d79597a5178-4e6a67354e324d77-595446694e6a6777-4e4459795a413d3d', 'licensekey': 'W12PgN03pIPpRqBYp5apMEpCmR1HVGQol0ByG0oktnaUmbLcAjSYq1dmEt4vHadWAPPuYf864RrXyrZn3s9m3E5Mv9wYlVTrUXQHKjcpvxxYLWeOaNRrloyIodIydtc9', 'activationDate': '1748070228.164', 'status': 'deactivate', 'application': 'Apna-Backup-Endpoint'}], 'awaited_Endpoints': [], 'last_updated': '1766756276.984708'}"
# import base64
# import re
# dagent=[]
# resj =  json.dumps(data) #res.text
# resj = re.sub(r"'(?P<key>\w+?)':", r'\"\g<key>\":', resj)  # For keys
# resj = re.sub(r":\s*'(?P<value>[^']*?)'", r':\"\g<value>\"', resj)  # For values
# resj = re.sub(r',\s*([\]}])', r'\1', resj)
# resj= json.loads(resj)
# d="D:\\"
# if type(resj) is str:
#     resj= json.loads(resj)
# if type(resj) is dict:
#     for dd in  resj.get("Endpoints", []):
#         try:
#             if not base64.b64decode(bytes.fromhex(dd.get("activationkey","").replace('-', ''))).decode("UTF-8") in dagent:
#                 dagent.append(base64.b64decode(bytes.fromhex(dd.get("activationkey","").replace('-', ''))).decode("UTF-8"))
#         except Exception as dwdw:
#             print(str(dwdw))
#     dagent=list(set(dagent))

#     from os import path
#     d= path.join(d,resj.get("server","SSSS").get("licensekey",""))
#     resj= json.dumps(resj)
            
# resj = base64.b64encode(resj.encode("UTF-8")).hex("-", 4)
# d = os.path.join(d, f"{d}.lic")
# import threading
# file_lock = threading.Lock()
# from builtins import open as fileopen
# with file_lock:
#     with fileopen(d, "wb") as encrypted_file:
#         encrypted_file.write(resj.encode("UTF-8"))
#         encrypted_file.close()


# try:

#     with file_lock:
#         # 'd' must be a string representing the file path
#         #with open(d, "wb") as encrypted_file:
#         try:
#             encrypted_file= fileopen(d, "wb")
#             # .encode() converts the string to bytes, which "wb" mode requires
#             encrypted_file.write(resj.encode("UTF-8"))
#         except Exception as dddd:
#             print(str(dddd))
#         finally:
#             encrypted_file.close()
# except:
#         try:
#             with fileopen("D:\\ll.lic", "wb") as f:
#             # .encode() converts the string to bytes, which "wb" mode requires
#                 f.write(resj.encode("UTF-8"))
#         except Exception as s:
#             print(str(s)) 

 
 
        
