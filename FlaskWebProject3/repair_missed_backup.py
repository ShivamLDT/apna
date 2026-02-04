"""
One-time repair: insert the missed GDrive backup record that failed with
'name xession is not defined' in save_savelogdata.

Uses data from the server log (e.g. structured_events.log line with
"all data comes in savelogdata") and optionally builds gidn_list from
temp chunk files if they still exist.

Run from FlaskWebProject3 folder:
  python repair_missed_backup.py

Optional:
  python repair_missed_backup.py --temp-dir "C:\\path\\to\\FlaskWebProject3\\temp\\received_chunks"
  python repair_missed_backup.py --db "C:\\path\\to\\5ea19afa....db"
"""
import argparse
import gzip
import json
import os
import sys
import time

# Data from the failed run (structured_events.log ~line 5065)
J_STA = 1770103674.917758
EPN = "DESKTOP-F1DRACU"
EPC = "5ea19afa4e2d68bbaca99c460d3ef34a00dfee042ba3e875bc3e6abe5358d3fd"
TCCSRC = "D:\\"  # from_computer path (original drive/path)
FILE_NAME = "AppnaBackup20GB.rar"
REP = "GDRIVE"
SIZE = 23145002162
PNAME = "Final Backup"
PIDTEXT = "1770103616.016775"
BKUP_TYPE = "full"
TOTAL_CHUNKS = 221  # chunk_index 221 was the one that failed
CHUNK_INDEX_WE_HAVE = 221
GIDN = {
    "id": "1EuBCdL0Tnv5191J5aCqI8mC5o1TBJJfo",
    "name": "AppnaBackup20GB.rar_221.gz_1770103674.917758.abgd",
    "mimeType": "text/abgd",
    "webViewLink": "https://drive.google.com/file/d/1EuBCdL0Tnv5191J5aCqI8mC5o1TBJJfo/view?usp=drivesdk",
    "sha256Checksum": "4e14328adf5b22f69443fcef22e3bf5f0b9af5a1bda0a0304870119b3e5cfeb7",
}
GIVN = "00000000000000000000000000000000"


def find_temp_chunk_dir(flask_project_root: str, upload_folder_name: str = "rapp") -> str:
    """Resolve temp dir for received chunks (same logic as add_unc_temppath)."""
    base = os.path.join(flask_project_root, upload_folder_name, "temp", "received_chunks")
    return base


def collect_gidn_list_from_temp(temp_base: str, tcc: str, file_name: str) -> list:
    """
    Scan temp chunk files (AppnaBackup20GB.rar_1.gz, ...), read each as gzip'd JSON (gfidi),
    return list of gidn dicts in chunk order. tcc is like "epc\\D{{DRIVE}}\\".
    """
    temp_dir = os.path.join(temp_base, tcc.replace("{{DRIVE}}", "DRIVE").rstrip("\\"))
    if not os.path.isdir(temp_dir):
        return []
    gidn_list = []
    prefix = f"{file_name}_"
    suffix = ".gz"
    by_idx = {}
    for fname in os.listdir(temp_dir):
        if not fname.startswith(prefix) or not fname.endswith(suffix):
            continue
        try:
            num = int(fname[len(prefix) : -len(suffix)])
        except ValueError:
            continue
        path = os.path.join(temp_dir, fname)
        try:
            with gzip.open(path, "rb") as f:
                raw = f.read().decode("utf-8", errors="ignore")
            data = json.loads(raw)
            by_idx[num] = data if isinstance(data, dict) else {"id": str(data)}
        except Exception:
            by_idx[num] = None
    if not by_idx:
        return []
    for i in range(1, max(by_idx.keys()) + 1):
        gidn_list.append(by_idx.get(i))
    return gidn_list


def main():
    parser = argparse.ArgumentParser(description="Insert missed GDrive backup record")
    parser.add_argument("--db", default=None, help="Path to agent .db file")
    parser.add_argument("--project-root", default=None, help="FlaskWebProject3 project root")
    parser.add_argument("--temp-dir", default=None, help="Temp received_chunks base dir (to build gidn_list)")
    parser.add_argument("--dry-run", action="store_true", help="Print SQL only, do not execute")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = args.project_root or script_dir
    db_path = args.db or os.path.join(project_root, f"{EPC}.db")
    if not os.path.isfile(db_path):
        print(f"DB not found: {db_path}")
        sys.exit(1)

    # Build gidn_list: try temp dir first; else use single known gidn at chunk 221
    gidn_list = []
    temp_base = args.temp_dir
    if not temp_base:
        for candidate in [
            os.path.join(project_root, "rapp", "temp", "received_chunks"),
            os.path.join(project_root, "FlaskWebProject3", "rapp", "temp", "received_chunks"),
        ]:
            if os.path.isdir(candidate):
                temp_base = candidate
                break
    if temp_base and os.path.isdir(temp_base):
        tcc = f"{EPC}\\D{{DRIVE}}\\"
        gidn_list = collect_gidn_list_from_temp(temp_base, tcc, FILE_NAME)
    if not gidn_list:
        # Fallback: one known gidn at index 220 (0-based), rest None
        gidn_list = [None] * TOTAL_CHUNKS
        if CHUNK_INDEX_WE_HAVE <= TOTAL_CHUNKS:
            gidn_list[CHUNK_INDEX_WE_HAVE - 1] = GIDN
        else:
            gidn_list.append(GIDN)
        print("No temp chunk files found; using single gidn (restore may be incomplete for missing chunks).")

    tcc_display = EPC + "\\D{{DRIVE}}\\"
    _original_path = (TCCSRC.rstrip(os.sep) + os.sep + FILE_NAME).replace("\\", "\\\\")
    data_repod_obj = {
        "gidn": GIDN,
        "givn": GIVN,
        "gidn_list": gidn_list,
        "path": TCCSRC,
        "file_name": FILE_NAME,
        "original_path": _original_path,
        "total_chunks": TOTAL_CHUNKS,
        "isMetaFile": False,
    }
    data_repod_val = json.dumps(data_repod_obj).replace("'", "''")
    now = int(time.time())
    # backups_M: one row per job
    sum_done = TOTAL_CHUNKS  # assume full for repair
    sql_main = (
        "INSERT INTO backups_M ("
        "id, date_time, from_computer, from_path, file_name, "
        "data_repo, mime_type, size, pNameText, pIdText, "
        "bkupType, sum_all, sum_done, done_all, mode, status, data_repod"
        ") VALUES ("
        f"{J_STA}, {now}, '{EPN}', '{TCCSRC.replace(chr(92), chr(92)+chr(92))}', "
        f"'{FILE_NAME}', "
        f"'{REP}', 'file', {SIZE}, "
        f"'{PNAME.replace(chr(39), chr(39)+chr(39))}', '{PIDTEXT.replace(chr(39), chr(39)+chr(39))}', '{BKUP_TYPE}', "
        f"{TOTAL_CHUNKS}, {sum_done}, 1, "
        "'xdone_all', 'xdone_all', '" + data_repod_val + "'"
        ") ON CONFLICT(id) DO UPDATE SET "
        "date_time=excluded.date_time, "
        "from_computer=excluded.from_computer, "
        "from_path=excluded.from_path, "
        "file_name=excluded.file_name, "
        "data_repo=excluded.data_repo, "
        "mime_type=excluded.mime_type, "
        "size=excluded.size, "
        "pNameText=excluded.pNameText, "
        "pIdText=excluded.pIdText, "
        "bkupType=excluded.bkupType, "
        "sum_all=excluded.sum_all, "
        "sum_done=excluded.sum_done, "
        "done_all=excluded.done_all, "
        "mode=excluded.mode, "
        "status=excluded.status, "
        "data_repod=excluded.data_repod"
    )

    # backups: one row per file in the job (id = unique per file, name = j_sta)
    backup_logs_id = J_STA + 0.0001  # unique id for this file row
    new_item = {
        "version": "26.1.12.1",
        "ip_address": EPC,
        "agent_name": EPN,
        "path": tcc_display,
        "file_name": FILE_NAME,
        "file_time": now,
        "size": SIZE,
        "rep": REP,
        "j_sta": J_STA,
        "pNameText": PNAME,
        "pIdText": PIDTEXT,
        "bkupType": BKUP_TYPE,
        "givn": GIVN,
        "gidn": GIDN,
        "metafile": False,
        "isMetaFile": False,
    }
    log_escaped = json.dumps(new_item).replace("'", "''")
    xdone_all = (sum_done * 100) / TOTAL_CHUNKS if TOTAL_CHUNKS else 100
    sql_logs = (
        "INSERT OR REPLACE INTO backups ("
        "id, name, date_time, from_computer, from_path, data_repo, "
        "mime_type, file_name, full_file_name, size, log, pNameText, "
        "pIdText, bkupType, sum_all, sum_done, done_all, mode, status"
        ") VALUES ("
        f"{backup_logs_id}, {J_STA}, {now}, '{EPN}', '{TCCSRC.replace(chr(92), chr(92)+chr(92))}', '{REP}', "
        f"'', '{FILE_NAME}', '{tcc_display.replace(chr(92), chr(92)+chr(92))}{FILE_NAME}', "
        f"{SIZE}, '{log_escaped}', "
        f"'{PNAME.replace(chr(39), chr(39)+chr(39))}', '{PIDTEXT.replace(chr(39), chr(39)+chr(39))}', '{BKUP_TYPE}', "
        f"{TOTAL_CHUNKS}, {sum_done}, '{xdone_all}', 'xdone_all', 'xdone_all'"
        ")"
    )

    if args.dry_run:
        print("-- backups_M:")
        print(sql_main[:500] + "...")
        print("-- backups:")
        print(sql_logs[:500] + "...")
        return

    # Run inserts (SQLiteManager may be in project_root or FlaskWebProject3 subfolder)
    try:
        for _path in [project_root, os.path.join(project_root, "FlaskWebProject3")]:
            if _path not in sys.path:
                sys.path.insert(0, _path)
        from sqlite_managerA import SQLiteManager
    except ImportError:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        cur = conn.cursor()
        cur.execute(sql_main)
        conn.commit()
        cur.execute(sql_logs)
        conn.commit()
        conn.close()
        print("Inserted (via sqlite3) into backups_M and backups.")
        return

    sm = SQLiteManager()
    qrs = [(db_path, [sql_main, sql_logs])]
    result = sm.execute_queries(qrs)
    if db_path in result:
        status_main = result[db_path][0][0]
        status_logs = result[db_path][1][0]
        if "success" in str(status_main).lower() and "success" in str(status_logs).lower():
            print("Inserted missed backup record into backups_M and backups.")
        else:
            print("Insert may have failed:", result)
    else:
        print("Unexpected result:", result)


if __name__ == "__main__":
    main()
