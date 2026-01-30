import argparse
import zlib
import struct
import json
import sys

# Define a custom secret key to validate the extraction process
SECRET_KEY = "mypassword"

# Define a custom header format
# This will store metadata length, data length, and compressed data
HEADER_FORMAT = "I I"  # 4-byte integer for metadata length and data length

# Function to create a compressed file with metadata
def create_compressed_exe(data, metadata, output_file):
    # Compress the data
    compressed_data = zlib.compress(data.encode())

    # Convert metadata to JSON and then to bytes
    metadata_bytes = json.dumps(metadata).encode()

    # Write custom header: (metadata length, data length)
    header = struct.pack(HEADER_FORMAT, len(metadata_bytes), len(compressed_data))

    # Combine header, metadata, and compressed data
    with open(output_file, "wb") as f:
        f.write(header)            # Write the header first
        f.write(metadata_bytes)    # Write the metadata
        f.write(compressed_data)   # Write the compressed data

    print(f"Executable '{output_file}' created successfully with metadata.")

# Function to extract data and metadata from a file
def extract_data_from_exe(input_file, password):
    try:
        with open(input_file, "rb") as f:
            # Read the custom header
            header = f.read(struct.calcsize(HEADER_FORMAT))
            metadata_len, data_len = struct.unpack(HEADER_FORMAT, header)

            # Read the metadata
            metadata_bytes = f.read(metadata_len)
            metadata = json.loads(metadata_bytes.decode())

            # Validate the password
            if password != SECRET_KEY:
                print("Invalid password.")
                return

            # Read and decompress the data
            compressed_data = f.read(data_len)
            data = zlib.decompress(compressed_data).decode()

            print("Data extracted successfully:")
            print("Metadata:", metadata)
            print("Data:", data)

    except Exception as e:
        print(f"Error extracting data: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compressed Data EXE with Metadata")
    parser.add_argument("--create", help="Create a compressed exe file", action="store_true")
    parser.add_argument("--extract", help="Extract data from the exe file", action="store_true")
    parser.add_argument("--file", help="The exe file to process", required=True)
    parser.add_argument("--data", help="Data to compress (for creating an exe)")
    parser.add_argument("--password", help="Password for extraction", required=False)
    parser.add_argument("--metadata", help="Metadata for the file (in JSON format)")

    args = parser.parse_args()

    if args.create and args.data and args.metadata:
        # Parse the provided metadata as JSON
        metadata = json.loads(args.metadata)
        # Create a compressed executable with the provided data and metadata
        create_compressed_exe(args.data, metadata, args.file)
    elif args.extract and args.password:
        # Extract data and metadata from the exe file using the provided password
        extract_data_from_exe(args.file, args.password)
    else:
        print("Invalid arguments. Use --help for more information.")
