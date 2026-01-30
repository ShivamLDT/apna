import argparse
import os
import sys
from lans import NetworkShare  


def main():
    parser = argparse.ArgumentParser(description="CLI tool to interact with a Windows SMB network share.")
    parser.add_argument("--host", required=True, help="Hostname or IP of the network share server.")
    parser.add_argument("--share", required=True, help="Name of the shared folder.")
    parser.add_argument("--user", required=True, help="Username for authentication.")
    parser.add_argument("--password", required=True, help="Password for authentication.")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    subparsers.add_parser("connect", help="Test and establish a connection to the network share.")
    subparsers.add_parser("disconnect", help="Disconnect from the share.")

    copy_parser = subparsers.add_parser("copy", help="Copy files to network share.")
    copy_parser.add_argument("--source", required=True, help="Source folder on local machine.")
    copy_parser.add_argument("--target", required=True, help="Target folder name on share.")

    json_parser = subparsers.add_parser("json", help="Create JSON of file paths on share.")
    json_parser.add_argument("--output", required=True, help="Output JSON file path.")
    json_parser.add_argument("--folderonly", action="store_true", help="Include only folders.")
    json_parser.add_argument("--level", type=int, default=2, help="Depth of recursion.")

    subparsers.add_parser("list", help="List shares and their metadata.")

    args = parser.parse_args()

    share = NetworkShare(args.host, args.share, args.user, args.password)

    if args.command == "connect":
        success = share.connect()
        print("Connection status:", "Success" if success else "Failed")

    elif args.command == "disconnect":
        share.disconnect()
        print("Disconnected.")

    elif args.command == "copy":
        share.connect()
        share.copy_files(args.source, args.target)
        share.disconnect()

    elif args.command == "json":
        share.connect()
        share.create_file_paths_json(args.output, folderonly=args.folderonly, level=args.level)
        share.disconnect()

    elif args.command == "list":
        share.connect()
        share.get_shared_list()
        share.disconnect()


if __name__ == "__main__":
    if os.name != 'nt':
        print("This tool only works on Windows.")
        sys.exit(1)
    main()

