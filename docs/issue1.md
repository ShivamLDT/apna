# fixed by shivam

# UNC/SMB3 Backup Selection – Implementation Documentation

## The Problem

The application fails to select or use a backup destination hosted on UNC paths, including Linux shared folders, Windows shared folders, and NAS storage, when accessed using the SMB3 protocol.

**Performance Requirement:** Backup to UNC destinations over SMB3 (Linux / Windows Shared Folders / NAS) should be able to complete 500 GB of data within a maximum of 8 hours, with stable throughput and zero backup failures, across all supported platforms.

---

## Initial Goal

1. **Client (fClient):** Replace SFTP validation with SMB-based validation; ensure `getConn()` accepts UNC shares when credentials are valid.
2. **Server (FlaskWebProject3):** Update SMB share listing for SMB3; ensure `browseUNC` works for SMB3-only shares.
3. **UNC path correctness:** Normalize UNC paths, handle long path prefixes (`\\?\UNC\`), avoid incorrect path joins.
4. **Backup status:** Include UNC in backup progress aggregation queries.
5. **Unified logging:** Single UNC/SMB lifecycle log file (`unc.log`) for both client and server.

---

## Functions Changed or Added

### Client (fClient)

| Function | File Path |
|----------|-----------|
| `normalize_unc_path` | `fClient/fClient/unc/lans.py` |
| `parse_unc_components` | `fClient/fClient/unc/lans.py` |
| `build_unc_path` | `fClient/fClient/unc/lans.py` |
| `NetworkShare.test_connection` | `fClient/fClient/unc/lans.py` |
| `NetworkShare.connect_smb` | `fClient/fClient/unc/lans.py` |
| `NetworkShare.disconnect_smb` | `fClient/fClient/unc/lans.py` |
| `getConn` | `fClient/fClient/views.py` |
| `restoretest` / `restoretest2` (UNC block, `_unc_restore_progress_cb`, `tccx_start_index`) | `fClient/fClient/views.py` |
| `decrypt_and_reassemble_file` | `fClient/fClient/unc/lans2.py` |
| `get_chunk_size` (adaptive 4MB/16MB) | `fClient/fClient/unc/smbwrapper.py` |
| `_upload_file_Bytes` (upload logic) | `fClient/fClient/unc/lans2.py` |
| `download_from_server` | `fClient/fClient/unc/lans2.py` |
| `upload_to_server` | `fClient/fClient/unc/lans2.py` |
| `storeFile` | `fClient/fClient/unc/smbwrapper.py` |
| `ensure_connected` | `fClient/fClient/unc/smbwrapper.py` |
| `ensure_remote_folder` | `fClient/fClient/unc/smbwrapper.py` |
| `create_remote_folder_recursive` | `fClient/fClient/unc/smbwrapper.py` |
| `mask_credentials` | `fClient/fClient/unc/unc_logger.py` |
| `log_connection_attempt` | `fClient/fClient/unc/unc_logger.py` |
| `log_connection_result` | `fClient/fClient/unc/unc_logger.py` |
| `log_path_normalization` | `fClient/fClient/unc/unc_logger.py` |
| `log_browse_start` / `log_browse_result` | `fClient/fClient/unc/unc_logger.py` |
| `log_transfer_start` / `log_transfer_complete` | `fClient/fClient/unc/unc_logger.py` |
| `log_share_list` | `fClient/fClient/unc/unc_logger.py` |
| `log_error` / `log_info` / `log_debug` | `fClient/fClient/unc/unc_logger.py` |

### Server (FlaskWebProject3)

| Function | File Path |
|----------|-----------|
| `normalize_unc_path` | `FlaskWebProject3/lans.py` |
| `parse_unc_components` | `FlaskWebProject3/lans.py` |
| `build_unc_path` | `FlaskWebProject3/lans.py` |
| `NetworkShare.test_connection` | `FlaskWebProject3/lans.py` |
| `NetworkShare.test_smb_connection` | `FlaskWebProject3/lans.py` |
| `browseUNC` | `FlaskWebProject3/FlaskWebProject3/views.py` |
| `get_restore_data` (UNC restore flow, `tccx`/`tccn`, manifest) | `FlaskWebProject3/FlaskWebProject3/views.py` |
| `handle_backup_data` | `FlaskWebProject3/FlaskWebProject3/views.py` |
| `log_browse_unc_request` | `FlaskWebProject3/unc_logger.py` |
| `log_error` / `log_info` | `FlaskWebProject3/unc_logger.py` |

---

## Implementation Summary

### 1. Client-Side (fClient)

- **SFTP → SMB validation:** Replaced paramiko/SFTP (port 22) with SMB-based validation in `NetworkShare.test_connection()` using `SMBConnection` with NTLMv2 and direct TCP (port 445). Works with SMB3-only shares (Linux Samba, Windows, NAS).
- **`getConn()`:** Uses `NetworkShare(...).test_connection()` for UNC. If primary credentials fail, falls back to `CredentialManager` and retests with stored credentials. Returns `EncryptedFileSystem` only when SMB test succeeds.
- **UNC path utilities:** Added `normalize_unc_path`, `parse_unc_components`, `build_unc_path` in `lans.py` for consistent UNC handling, long path prefix `\\?\UNC\`, and avoiding double backslashes.
- **Restore path handling:** Introduced `tccx_start_index` in `views.py` so restore target paths keep the drive letter (e.g. `C:\Users\...`). Previously `start_index` from `tccn` incorrectly stripped the drive from `tccx`.
- **Drive letter fallback:** In `lans2.py`, if `restore_path` lacks a drive letter on Windows (e.g. `Users\LDT\Documents\...`), it is prefixed with `SystemDrive` (e.g. `C:\Users\...`).
- **Post-upload checksum:** Chunks are read back from the share after upload; hash is compared to expected. On mismatch, upload is retried.
- **Download checksum and retries:** Removed the bypass that overwrote `chunk_hash` with `expected_hash`. Added checksum verification and up to 3 retries with backoff on mismatch.
- **Progress callback:** `decrypt_and_reassemble_file` accepts `progress_callback(chunk_idx, total_chunks, progress_pct)` and calls it after each chunk. Progress goes 0→100 (completed fraction).
- **File existence check:** `decrypt_and_reassemble_file` raises if the restored file does not exist. `views.py` checks `os.path.isfile(restore_target)` before returning success for UNC.
- **SMB chunk size:** Adaptive chunk size in `smbwrapper.py` – 4 MB for localhost, 16 MB for remote – to reduce SMB throttling.
- **Upload retries:** `BytesIO.seek(0)` before retries; fallback writes chunk to local disk when SMB upload fails; `ensure_remote_folder` with correct parent path.

### 2. Server-Side (FlaskWebProject3)

- **SMB3 support:** `NetworkShare.test_smb_connection()` uses `SMBConnection` with NTLMv2 and direct TCP for SMB3 negotiation. `test_connection()` tries SMB first, then WNet.
- **`browseUNC`:** Uses `NetworkShare` and UNC logging. Supports `trace`, `browse`, and `shares` methods. Logs requests with masked credentials.
- **UNC in backup progress:** Removed exclusions like `data_repo not in ('UNC')` in backup progress aggregation in `views.py`.
- **UNC restore path:** For UNC storage type, `tccx` and `tccn` are built from `RestoreLocation` with `{{DRIVE}}` placeholder instead of complex path replacements that produced bad paths.
- **UNC manifest:** UNC restores build manifest from `jsrepd` (DB metadata), not from a local manifest file.
- **Restore success validation:** `files_restored` is incremented only when the client response body has `restore == "success"`, not just on HTTP 200/201.

### 3. UNC Path Correctness

- **Normalization:** `normalize_unc_path` handles `\\?\UNC\` prefix, strips extra backslashes, and normalizes separators.
- **Drive-at-end fix:** When the path ends with `\C:` (drive at end), client-side logic in `views.py` moves the drive to the front (e.g. `C:\Users\...`).
- **`{{DRIVE}}` placeholder:** Server replaces `:` with `{{DRIVE}}` in paths; client decodes and replaces `{{DRIVE}}` with `:`.

### 4. Unified Logging

- **Logger module:** `fClient/fClient/unc/unc_logger.py` and `FlaskWebProject3/unc_logger.py` provide UNC/SMB logging.
- **Log file:** `FlaskWebProject3/every_logs/unc.log` and `fClient/every_logs/unc.log`.
- **Events logged:** `browseUNC`, connection attempt/result, masked credentials, path normalization, transfer start/end, errors, throughput, share list.

---

## UI Changes

### Restore Progress Bar Stuck at 0%

**What was wrong:**  
- UNC restore progress callback sent `progress_pct = 100 * (total_chunks - chunk_idx) / total_chunks` (100→0).  
- `Restorepp.jsx` used `displayProgressValue = 0` when `restore_accuracy` was not set.

**What was fixed:**
- In `lans2.py`, progress formula changed to `100 * chunk_idx / total_chunks` (0→100).
- In `Restorepp.jsx`, when `restore_accuracy` is missing (UNC case), use `progress_number` for `displayProgressValue`.

### Job-Level Progress Frozen at 0% While File Showed 18.9%

**What was wrong:**  
When `status === "counting"` and `filename` were present, the UI treated it as file-level and froze job-level `progress_number` at `previousJob?.progress_number` (0).

**What was fixed:**
- In `Restorepp.jsx`, only freeze job progress when `restore_accuracy` is present (server-side aggregation).
- For UNC chunk-level updates (no `restore_accuracy`), use `job.progress_number` for the job level so it matches file progress.

### Progress Bar Disappeared on Refresh

**What was wrong:**  
The Refresh button cleared all `localStorage` (backup and restore), removing in-progress restore state.

**What was fixed:**
- In `ProgressBarChart.jsx`, `handleRefresh` clears only backup-related items (`storedAgentDataa`, `storedAnimatedDataa`, `storedJobFiles`) when on the Backup tab.
- Restore items (`storedRestoreAgentData`, `storedRestoreAnimatedData`, `storedRestoreJobFiles`) are preserved when on the Restore tab.

### Files and Functions Touched for UI

| Function | File |
|----------|------|
| `handleRefresh` | `LatestFrontendCode(05-01-2025)/src/Components/Progress/ProgressBarChart.jsx` |
| `backup_data` socket handler (animatedData, shouldFreezeJobProgress, displayProgressValue) | `LatestFrontendCode(05-01-2025)/src/Components/Progress/Restorepp.jsx` |

---

## Additional Fixes During Session

| Issue | Fix |
|-------|-----|
| Malformed path `Users\...\FlaskWebProject3_130126.rar\C:` | Server `tccx` construction for UNC; client path normalization (drive-at-end). |
| Manifest missing for UNC restore | Build manifest from `jsrepd` instead of reading local manifest. |
| `STATUS_SHARING_VIOLATION`, `No such file or directory` | `BytesIO.seek(0)` before retries; uncommented fallback chunk write; fixed `ensure_remote_folder` path. |
| `'builtin_function_or_method' object has no attribute 'uniform'` | Changed `from random import random` to `import random` in `smbwrapper.py`. |
| SMB throttled warnings | Adaptive chunk size (4 MB local, 16 MB remote) in `smbwrapper.py`. |
| `RETRY_ATTEMPTS` undefined | Use `len(RETRY_LIMIT)` in `lans2.py`. |
| Restore reported success but file missing | Server checks response body for `restore == "success"`; client verifies file exists before returning success. |
