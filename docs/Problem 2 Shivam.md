#The Problem :
Large files and folders (like greater than 20 GB) appear to be backed up successfully across all destinations. However, during restoration, files fail due to missing chunks, resulting in partial or corrupted restores. Even though the backup status shows successful completion, large files and folders are not fully restored across any destination, impacting data integrity.


#The Solution:
# Chunk checksum and cloud storage (GDrive, S3, Azure)

## Integrity at every step

We verify that chunks are **complete and correct** in three places:

1. **Client** – We compute SHA-256 (`chkh`) of the compressed chunk before send.
2. **Server** – We verify what we received (compare computed hash to `chkh`; for GDrive we compare Drive’s `sha256Checksum` to `chkh`).
3. **Cloud (GDrive / S3 / Azure)** – We ensure what **landed** in the cloud matches what we sent.

Without (3), we would not know if the chunk was corrupted in transit to the cloud or stored incorrectly. All three clouds now participate in integrity verification.

---

## Integrity at the cloud (chunks received by AWS, Azure, GDrive)

| Cloud   | How we verify what they received | Result if mismatch |
|---------|-----------------------------------|--------------------|
| **GDrive** | Client uploads chunk → Drive returns `sha256Checksum` → we compare to `chkh` on the server. | Server logs mismatch and can fail the chunk. |
| **S3**     | Server sends **ChecksumSHA256** (SHA-256 of chunk) with PutObject. **S3 validates** the upload against it and rejects the request if the stored bytes don’t match. | Upload fails; we don’t mark the chunk as stored. |
| **Azure**  | Server sends **Content-MD5** (MD5 of chunk) with the blob. **Azure validates** the upload and rejects if the stored bytes don’t match. | Upload fails; we don’t mark the chunk as stored. |

So:

- **GDrive**: We get Drive’s checksum and compare (no download). Same algorithm as `chkh` (SHA-256).
- **S3**: We send a checksum with the upload; S3 guarantees what is stored matches that checksum (SHA-256).
- **Azure**: We send Content-MD5 with the upload; Azure guarantees what is stored matches that MD5.

We **do** verify the integrity of the chunks where they ultimately end (GDrive, S3, Azure).

---

## No-download verification (GDrive)

For GDrive we **do not download the file** to check the checksum. The client uploads the chunk to Drive; the Drive API returns `sha256Checksum` in the create response. The client sends that (with `chkh`) in the `gfidi` header; the server compares them.

---

## Algorithm alignment

| Where        | Algorithm | Notes |
|-------------|-----------|--------|
| **Client**  | SHA-256   | `chkh` = `hashlib.sha256(compressed_chunk).hexdigest()` |
| **GDrive**  | SHA-256   | `sha256Checksum` in file metadata – same as `chkh` |
| **S3**      | SHA-256   | **ChecksumSHA256** sent with PutObject; S3 validates and stores only if it matches |
| **Azure**   | MD5       | **Content-MD5** (bytearray) sent with blob; Azure validates and rejects on mismatch |

---

## Current flow: S3 and Azure

For **AWSS3** and **AZURE**, the client sends the chunk to the server (`POST` with `files=...`). The server:

1. Verifies the received chunk (SHA-256 vs `chkh`).
2. Uploads to S3 or Azure **with** ChecksumSHA256 or Content-MD5 so the cloud verifies what it stores.

So we verify both **client → server** and **server → cloud**.

---

## Process: LAN

For **LAN / Local storage**, the client sends the chunk in the request body (`POST` with `files=...`) and the `chkh` header. The server receives the chunk, computes SHA-256 of the received bytes, and compares to `chkh`. If they match, the chunk is written to the local or LAN path. There is no cloud step; integrity is verified at **client → server** only.

---

## Summary

1. **LAN**: Client sends chunk to server; server verifies SHA-256 vs `chkh` and writes to local/LAN. No cloud; integrity at server = verified.
2. **GDrive**: Client uploads to Drive; we compare Drive’s `sha256Checksum` to `chkh` (no download). Integrity at cloud = verified.
3. **S3**: Server uploads with **ChecksumSHA256**; S3 validates. Integrity at cloud = verified (upload fails if mismatch).
4. **Azure**: Server uploads with **Content-MD5**; Azure validates. Integrity at cloud = verified (upload fails if mismatch).

---

## Functions Added

All functions that **compute**, **verify**, **store**, or **expose** checksums/hashes for backup integrity.

### Client – calculation and sending

| Path | Function / location | Role |
|------|----------------------|------|
| `fClient/fClient/sjbs/class1x.py` | `hash_file` | SHA-256 of whole file (chunk_size 128KB). |
| `fClient/fClient/sjbs/class1x.py` | Backup flow (file_hasher, chunk_hash) | File hasher (SHA-256) over stream; chunk_hash = SHA-256 of compressed chunk; sets headers `chkh`, `filehash`. |
| `fClient/fClient/sjbs/class2.py` | Backup flow (file_hasher, chunk_hash) | File hasher (SHA-256) over chunks; chunk_hash = SHA-256 of chunk; sets headers `chkh`, `filehash`. |
| `fClient/fClient/unc/lans2.py` | Chunk upload paths | `chunk_hash = hashlib.sha256(encrypted_chunk).hexdigest()`; compare to `expected_hash` on verify. |
| `fClient/fClient/xxh.py` | `_hash_file`, `hash_file`, `hash_folder` | File/folder hashing (xxhash or blake3) for integrity; `hash_file` used in flow. |
| `fClient/fClient/module3.py` | Upload block | `file_hash = hashlib.sha256(file_data).hexdigest()`; sent as `hash`. |
| `fClient/module13.py` | Upload block | `file_hash = hashlib.sha256(file_data).hexdigest()`; sent as `hash`. |

### Client – verification (restore)

| Path | Function / location | Role |
|------|----------------------|------|
| `fClient/fClient/views.py` | Restore / merge blocks | Builds `file_hasher = hashlib.sha256()`, compares `actual_file_hash` to `chunk_manifest["file_hash"]`. |

### Client – GDrive (request Drive checksum)

| Path | Function / location | Role |
|------|----------------------|------|
| `fClient/gd/GDClient.py` | `upload_file` | Requests `sha256Checksum` in `fields` so Drive returns checksum; client sends it to server in `gfidi`. |

### Server – verification (upload_file)

| Path | Function / location | Role |
|------|----------------------|------|
| `FlaskWebProject3/FlaskWebProject3/views.py` | `upload_file` | Reads `chkh`, `filehash`; for non-GDrive: `computed_hash = hashlib.sha256(decompressed_chunk).hexdigest()` vs `chkh`; for GDrive: compares Drive `sha256Checksum` (from `gfidi`) to `chkh`; sets `checksum_mismatch` / `checksum_error` and logs `chunk_checksum_ok` / `chunk_checksum_failed`. |

### Server – manifest (load/save hashes)

| Path | Function / location | Role |
|------|----------------------|------|
| `FlaskWebProject3/FlaskWebProject3/views.py` | `_load_manifest` | Loads manifest (contains `chunks` (seq → chunk hash), `file_hash`). |
| `FlaskWebProject3/FlaskWebProject3/views.py` | `_save_manifest` | Saves manifest with `chunk_hash`, `file_hash` per chunk. |
| `FlaskWebProject3/FlaskWebProject3/views.py` | `_manifest_folder` | `hashlib.sha256(value.encode("utf-8")).hexdigest()` for manifest folder path when value is JSON-like. |
| `FlaskWebProject3/FlaskWebProject3/views.py` | `save_temp` | Writes manifest: `manifest["chunks"][seq_num] = chunk_hash`, `manifest["file_hash"] = file_hash`. |
| `FlaskWebProject3/FlaskWebProject3/views.py` | `get_restore_data` | Returns restore data including `chunks` (hashes) and `file_hash`. |

### Server – digest / hash API and helpers

| Path | Function / location | Role |
|------|----------------------|------|
| `FlaskWebProject3/FlaskWebProject3/views.py` | `calculate_file_digest` | Computes file digest (default SHA-512) in chunks; returns hex digest. |
| `FlaskWebProject3/FlaskWebProject3/views.py` | `calculate_file_digest_threaded` | Threaded wrapper for `calculate_file_digest` (e.g. MD5). |
| `FlaskWebProject3/FlaskWebProject3/views.py` | `calculate_hash` | Route `/api/calculatehash`: calls `calculate_file_digest_threaded`. |
| `FlaskWebProject3/FlaskWebProject3/views.py` | Restore/merge flows | `hash_function = hashlib.new("md5")`  for merged file; `file_code = hash_function.hexdigest()`. |

### Server – cloud upload (checksum sent to cloud)

| Path | Function / location | Role |
|------|----------------------|------|
| `FlaskWebProject3/awd/AWSClient.py` | `upload_data`, `upload_file` | Compute SHA-256 of payload, set `ChecksumSHA256` on S3 PutObject so S3 verifies at rest. |
| `FlaskWebProject3/azd/AzureClient.py` | `upload_data`, `upload_file` | Compute MD5 of payload, set `Content-MD5` on blob upload so Azure verifies at rest. |

