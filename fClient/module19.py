import argparse
import requests
def compare_hex(file1, file2):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        data1 = f1.read()
        data2 = f2.read()

        if data1 == data2:
            print(" Files are identical.")
            return
        
        print(f"{'Offset':<8} {'File1':<16} {'File2':<16}")
        print('-' * 40)

        for i in range(min(len(data1), len(data2))):
            b1 = data1[i]
            b2 = data2[i]

            if b1 != b2:
                offset = f"{i:08x}"
                print(f"{offset} {b1:02x} {b2:02x}")

        if len(data1) != len(data2):
            print("\n Files have different sizes!")
            extra_data = data1[len(data2):] if len(data1) > len(data2) else data2[len(data1):]
            offset = f"{min(len(data1), len(data2)):08x}"
            for i, b in enumerate(extra_data):
                print(f"{offset} {b:02x} {'--' if len(data1) > len(data2) else b:02x}")
                offset = f"{int(offset, 16) + 1:08x}"

def main():
    parser = argparse.ArgumentParser(
        description="Hex compare two binary files"
    )
    parser.add_argument('file1', help="Path to first file")
    parser.add_argument('file2', help="Path to second file")

    args = parser.parse_args()
    
    if not args.file1 or not args.file2:
        print(" Please provide two files to compare.")
        return
    
    try:
        compare_hex(args.file1, args.file2)
    except FileNotFoundError as e:
        print(f" {e}")
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    x= str("one Three, six SEVEN, Four").lower() \
    .replace("one","1")\
    .replace("two","2")\
    .replace("three","3")\
    .replace("four","4")\
    .replace("five","5")\
    .replace("six","6")\
    .replace("seven","7")\
    .replace("eight","8")\
    .replace("nine","9")\
    .replace("zero","1")\
    .replace(" ","").replace(",","")
    print(x)
    #main()
