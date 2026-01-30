import psutil
drive_info = []
try:
    partitions = psutil.disk_partitions(all=True)
    for partition in partitions:
        try:
            if (not partition.opts.__contains__("cdrom")) and (not partition.opts.__contains__("removable")>0):
                print(partition.opts)
                print(partition.mountpoint)
        except:
                print("Drive access error")
except Exception as wee:
    print(str(wee))
input("Press any key to continue...")