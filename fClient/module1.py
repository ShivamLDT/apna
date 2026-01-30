import gzip
import bz2
import lzma
import zlib


def compress_with_gzip(input_filename, output_filename, compression_level):
    with open(input_filename, "rb") as f_in, gzip.open(
        output_filename, "wb", compresslevel=compression_level
    ) as f_out:
        f_out.writelines(f_in)


def compress_with_bzip2(input_filename, output_filename, compression_level):
    with open(input_filename, "rb") as f_in, bz2.open(
        output_filename, "wb", compresslevel=compression_level
    ) as f_out:
        f_out.writelines(f_in)


def compress_with_lzma(input_filename, output_filename, compression_level):
    with open(input_filename, "rb") as f_in, lzma.open(
        output_filename, "wb", preset=compression_level
    ) as f_out:
        f_out.writelines(f_in)


def compress_with_zlib(input_filename, output_filename, compression_level):
    with open(input_filename, "rb") as f_in, open(output_filename, "wb") as f_out:
        compressor = zlib.compressobj(compression_level)
        for chunk in iter(lambda: f_in.read(4096), b""):
            f_out.write(compressor.compress(chunk))
        f_out.write(compressor.flush())


def main():
    input_filename = "D:\\aaaaaaa.txt"
    output_base_filename = "D:\\aaaaaaa_txt\\output"
    compression_levels = [1, 5, 9]
    import threading

    # Perform compression using different techniques and compression levels
    jobs = []

    t = threading.Thread(
        target=compress_with_gzip,
        args=[input_filename, f"{output_base_filename}_gzip_{1}.gz", 1],
    )

    jobs.append(t)

    t = threading.Thread(
        target=compress_with_bzip2,
        args=[input_filename, f"{output_base_filename}_bzip2_{1}.bz2", 1],
    )

    jobs.append(t)
    t = threading.Thread(
        target=compress_with_lzma,
        args=[input_filename, f"{output_base_filename}_lzma_{1}.xz", 1],
    )
    jobs.append(t)
    t = threading.Thread(
        target=compress_with_zlib,
        args=[input_filename, f"{output_base_filename}_zlib_{1}.zlib", 1],
    )

    jobs.append(t)

    t = threading.Thread(
        target=compress_with_gzip,
        args=[input_filename, f"{output_base_filename}_gzip_{5}.gz", 5],
    )
    jobs.append(t)
    t = threading.Thread(
        target=compress_with_bzip2,
        args=[input_filename, f"{output_base_filename}_bzip2_{5}.bz2", 5],
    )
    jobs.append(t)
    t = threading.Thread(
        target=compress_with_lzma,
        args=[input_filename, f"{output_base_filename}_lzma_{5}.xz", 5],
    )
    jobs.append(t)
    t = threading.Thread(
        target=compress_with_zlib,
        args=[input_filename, f"{output_base_filename}_zlib_{5}.zlib", 5],
    )
    jobs.append(t)

    t = threading.Thread(
        target=compress_with_gzip,
        args=[input_filename, f"{output_base_filename}_gzip_{9}.gz", 9],
    )

    jobs.append(t)
    t = threading.Thread(
        target=compress_with_bzip2,
        args=[input_filename, f"{output_base_filename}_bzip2_{9}.bz2", 9],
    )

    jobs.append(t)
    t = threading.Thread(
        target=compress_with_lzma,
        args=[input_filename, f"{output_base_filename}_lzma_{9}.xz", 9],
    )

    jobs.append(t)
    t = threading.Thread(
        target=compress_with_zlib,
        args=[input_filename, f"{output_base_filename}_zlib_{9}.zlib", 9],
    )

    jobs.append(t)
    for j in jobs:
        j.start()


if __name__ == "__main__":
    main()
