import gzip
import json

def add_meta_info_to_gzip(filename, meta_data):
  """
  Adds meta data to an existing gzip file.

  Args:
    filename: Path to the gzip file.
    meta_data: Dictionary containing the meta data to be added.

  Raises:
    FileNotFoundError: If the specified gzip file does not exist.

  Returns:
    Path to the updated gzip file.
  """

  try:
    with gzip.open(filename, 'rb') as f_in:
      original_data = f_in.read()

    meta_data_json = json.dumps(meta_data).encode('utf-8') 

    # Combine original data with meta data
    updated_data = meta_data_json + b'\x00' + original_data 

    # Write updated data to a new gzip file
    with gzip.open(filename + '.updated01.gz', 'wb') as f_out:
      f_out.write(updated_data)


    return filename + '.updated01.gz'

  except FileNotFoundError:
    print(f"Error: Gzip file '{filename}' not found.")
    return None

# Example usage
meta_info = {
    "author": "John Doe",
    "date": "2024-11-28",
    "version": "1.0"
}

updated_filename = add_meta_info_to_gzip("D:\\avcodec.dll_1735371216.3338351.gz", meta_info)
if updated_filename:
  print(f"Meta data added successfully. Updated file: {updated_filename}")
