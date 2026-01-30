import pytsk3

# Open NTFS Drive
img = pytsk3.Img_Info(r"\\.\C:")
fs = pytsk3.FS_Info(img)

# Iterate through NTFS File Table
for file in fs.open_dir(path="/"):
    if file.info.meta and file.info.meta.flags & pytsk3.TSK_FS_META_FLAG_UNALLOC:
        print(f" Deleted File Found: {file.info.name.name.decode()}")
        recovered_file = f"recovered_{file.info.name.name.decode()}"
        
        # Recover the file
        with open(recovered_file, "wb") as f:
            f.write(file.read_random(0, file.info.meta.size))
        print(f" File Recovered: {recovered_file}")
print("Done")