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
