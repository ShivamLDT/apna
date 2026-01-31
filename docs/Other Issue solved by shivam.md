# Issues Solved (Summary)

1) Restore online/offline mismatch
Problem: Restore page showed Offline while Endpoints showed Online.
Root cause: /refreshclientnodes only emits a socket event (no refresh), /restore_nodes used stale lastConnected timestamps, and the UI inverted "True".
Solution: Use is_less_than_2_minutes for live checks and render "True" as Online.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `restore_nodes()` (uses is_less_than_2_minutes) and `refresh_client_nodes()` (broadcast-only); LatestFrontendCode(05-01-2025)/src/Components/Restore/Restore.jsx (status render/sort).
Result: Restore and Endpoints pages show consistent status.
---
2) Backup failure not reflected in progress UI
Problem: Backup progress stayed "in progress" after a chunk failed.
Root cause: Failure was only returned via HTTP and not emitted over websocket.
Solution: Emit backup_data with status "failed" and error code when chunk handling fails.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `upload_file()` (backup_data emit on failure).
Result: UI shows Failed immediately.
---
3) Restore fetch crash (UnboundLocalError)
Problem: /restore action=fetch crashed with UnboundLocalError for agent_candidates.
Root cause: agent_candidates was only set in the fetchAll branch.
Solution: Initialize agent_candidates before the fetch/fetchAll split.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `get_restore_data()`.
Result: Fetch returns 200 instead of 500.
---
4) Restore fetch errors hidden in UI
Problem: Restore UI showed no error when fetch failed.
Root cause: catch block did not surface the error message.
Solution: Set alert message and keep restore area visible.
What changed: LatestFrontendCode(05-01-2025)/src/Components/Restore/Restore.jsx `postData` catch.
Result: Users see the failure reason.
---
5) Restore fetch returned 0 due to DB path variance
Problem: Restore list was empty even though backups existed.
Root cause: DB path discovery tried too few extensions and names.
Solution: Try multiple extensions and base names and scan the location folder.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `get_restore_data()` (fetch path discovery).
Result: Restore fetch finds metadata reliably.
---
6) GDrive backups missing in backups_M (no schema)
Problem: GDrive backups uploaded but did not appear in restore.
Root cause: save_savelogdata wrote to a no-extension DB without backups_M table.
Solution: Ensure schema exists by calling create_database(dbname).
What changed: FlaskWebProject3/FlaskWebProject3/views.py `save_savelogdata()`; FlaskWebProject3/module2.py `create_database()`.
Result: New cloud backups appear in restore.
---
7) GDrive/OneDrive backups not finalized
Problem: Cloud backups did not finalize; metadata was not stored.
Root cause: save_all expected local temp chunks for cloud-only backups.
Solution: Pass bGD_backup and bOneDrive_backup to save_all.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `upload_file()` -> `save_all(...)`.
Result: Cloud backups finalize and persist metadata.
---
8) Backup UI showed Completed on failure
Problem: Failed backups still displayed Completed/100 percent.
Root cause: completed logic ignored failed status.
Solution: Treat failed as not completed in all status calculations.
What changed: LatestFrontendCode(05-01-2025)/src/Components/Progress/Backupp.jsx (`getStatusIcon`, `getStatusText`, card isCompleted).
Result: Failed jobs show red and not Completed.
---
9) Backup job card appeared late
Problem: Backup card appeared only after first backup_data.
Root cause: "starting" socket event did not populate animatedData.
Solution: Update animatedData immediately on "starting" and persist it.
What changed: LatestFrontendCode(05-01-2025)/src/Components/Progress/Backupp.jsx (starting socket handler).
Result: Job card appears as soon as backup starts.
---
10) Browse action ignored backups_M (cloud)
Problem: Browse showed empty list for cloud backups.
Root cause: action=browse queried only backups table.
Solution: Query backups_M first and build file_paths, fallback to backups.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `get_restore_data()` (browse branch).
Result: Browse lists cloud files.
---
11) Restore action ignored backups_M rows and used wrong target path
Problem: Restore loop skipped backups_M rows and used wrong folder.
Root cause: qresults[0] empty but used; row shape mismatched; path parsing did not match target.
Solution: Use qresults[1] when needed, normalize rec_dict, and match file segment in _tcc_value to derive _rec_fpath.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `get_restore_data()` (restore loop).
Result: Restore runs for cloud rows and uses the correct target folder.
---
12) Cloud restore without local manifest
Problem: Cloud restores failed when manifest files were missing on server.
Root cause: Restore assumed a disk manifest existed.
Solution: Use backups_M.data_repod JSON as restore payload and build manifest in memory.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `get_restore_data()`; FlaskWebProject3/module2.py `BackupMain.data_repod` (existing column).
Result: Cloud restores work without local manifests.
---
13) Server 500 after client disconnect
Problem: Server returned 500 when client closed the connection.
Root cause: res.json() was called even when requests.post failed and res was unset.
Solution: Guard res.json() and return a clean failed response with reason.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `get_restore_data()` (restoretest request).
Result: Server returns a valid failure response instead of 500.
---
14) Client restoretest crash (file_metada None)
Problem: Client closed the connection without response during cloud restore.
Root cause: file_metada was None and len(None) raised TypeError.
Solution: Build file_metada from chunk_manifest keys or 1..total_chunks when missing.
What changed: fClient/fClient/views.py `restoretest()`.
Result: Client responds correctly; restore continues.
---
15) GDrive gidn_list format wrong (single-chunk)
Problem: gidn_list stored as list(gidn.values()) caused client errors.
Root cause: Single-chunk gidn is a dict and was converted incorrectly.
Solution: Store gidn_list as [gidn] and normalize on restore; log and return client 5xx reason.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `save_all()` and `get_restore_data()`.
Result: Existing backups restore and the UI shows real error reasons.
---
16) Restore status and notifications accurate
Problem: UI showed success even when restore failed and sometimes duplicated toasts.
Root cause: Backend always sent "restored" and frontend treated finished as completed.
Solution: Send "restored" only on full success, emit final backup_data status, and gate success toast on completed.
What changed: FlaskWebProject3/FlaskWebProject3/views.py (restore completion emit); LatestFrontendCode(05-01-2025)/src/Components/Progress/Restorepp.jsx (toast/status); LatestFrontendCode(05-01-2025)/src/Components/Restore/RestoreData/RestoreData.jsx (start notification).
Result: Restore status and notifications are accurate.
---
17) Restore error reason visible in UI
Problem: 500 errors showed only a generic message.
Root cause: UI did not extract the reason field from the response.
Solution: Include reason on server response and prefer result[0].reason in frontend.
What changed: FlaskWebProject3/FlaskWebProject3/views.py (reason in response); LatestFrontendCode(05-01-2025)/src/Components/Restore/RestoreData/RestoreData.jsx (error parsing).
Result: UI displays the actual failure cause.
---
18) Manifest file_hash missing -> FILE_CHECKSUM_MISMATCH
Problem: Client rejected restore due to missing file_hash.
Root cause: Cloud restore manifest was built without loading disk manifests or temp manifests.
Solution: Load manifest_path when present, search temp dirs (UNC/non-UNC and upload folder), copy best manifest to final path, and fallback to hash keys in jsrepd. Add restore_manifest_selected logging.
What changed: FlaskWebProject3/FlaskWebProject3/views.py `get_restore_data()` (manifest load/search) and structured logging.
Result: Client receives file_hash and restore succeeds.
---
19) py7zr restore compatibility
Problem: AttributeError for readall/read in some py7zr versions.
Root cause: Code assumed those methods existed.
Solution: Fallback to extractall into temp dir and read files if readall/read are missing.
What changed: fClient/fClient/p7zstd.py `decompress()`.
Result: Decompression works across py7zr versions.
