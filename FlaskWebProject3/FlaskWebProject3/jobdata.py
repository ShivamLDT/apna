import gzip
import json
import sqlite3
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta

from flask import jsonify

from fingerprint import getCode
class JobsRecordManager:
    def __init__(self, db_name: str, json_file: str,app: object):
        self.db_name = str(app.config.get("getCode",None))
        self.json_file = json_file
        self.records = []
        # Create database connection and table if it doesn't exist
        self.conn = sqlite3.connect(self.db_name)
        ##kartik
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('PRAGMA synchronous=NORMAL')
        self.conn.execute('PRAGMA busy_timeout=30000')  
        self.conn.execute('PRAGMA temp_store=MEMORY')
        self.conn.execute('PRAGMA cache_size=-64000')
        ##kartik
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs_recordManager (
                    idx TEXT,
                    agent TEXT,
                    name TEXT,
                    id TEXT,
                    src_path TEXT,
                    data_repo TEXT,
                    next_run_time TEXT,
                    created_at TEXT
                )
            ''')

    def alter_table(self, column_name: str, column_type: str):
        with self.conn:
            try:
                self.conn.execute(f'ALTER TABLE jobs_recordManager ADD COLUMN {column_name} {column_type};')
            except sqlite3.OperationalError as e:
                print(f"Error altering table: {e}")

    def add_records(self, records: List[Dict]):
        self.records = records
        #self.save_to_json()
        self.save_to_db()

    def save_to_json(self):
        # Convert created_at to float for sorting and filtering
        for record in self.records:
            record['created_at'] = float(record['created_at'])

        # Sort records by created_at in descending order
        sorted_records = sorted(self.records, key=lambda x: x['created_at'], reverse=True)

        # Group records by time difference (within 3 minutes)
        grouped_records = []
        latest_time = None

        for record in sorted_records:
            if latest_time is None or (latest_time - record['created_at'] <= 180):
                # Append the record to the current group
                grouped_records.append(record)
            else:
                # Break if the difference is greater than 180 seconds
                break
            latest_time = record['created_at']

        # Keep only the top 10 ranks
        top_ranked = grouped_records[:10]
        
        # Grouping the records in the desired JSON format
        grouped_data = {}
        for record in top_ranked:
            idx = record['idx']
            agent = record['agent']
            name = record['name']
            id_ = record['id']

            if idx not in grouped_data:
                grouped_data[idx] = {}

            if agent not in grouped_data[idx]:
                grouped_data[idx][agent] = {}

            grouped_data[idx][agent][name] = id_

        with open(self.json_file, 'w') as f:
            json.dump(grouped_data, f, indent=4)
    
    def save_to_db(self):
        with self.conn:
            self.conn.executemany('''
                INSERT INTO jobs_recordManager (idx, agent, name, id, src_path, data_repo, next_run_time, created_at)
                VALUES (:idx, :agent, :name, :id, :src_path, :data_repo, :next_run_time, :created_at)
            ''', self.records)

    def load_from_json(self) -> Dict:
        with open(self.json_file, 'r') as f:
            return json.load(f)

    def fetch_all_records(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM jobs_recordManager")
        rows = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

    def format_epoch_to_ist(self,epoch_time):
        dt = datetime.fromtimestamp(float(epoch_time), tz=timezone.utc)
        ist_dt = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
        return ist_dt.strftime('%d-%m-%Y %H:%M:%S')

    def format_next_run_time(self,next_run_time_str):
        dt = datetime.fromisoformat(next_run_time_str.replace("Z", "+00:00"))
        ist_dt = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
        return ist_dt.strftime('%d-%m-%Y %H:%M:%S %z')
    def fetch_jobs_as_json(self,n=10):
        cursor =self.conn.cursor()
        cursor.execute(f"SELECT agent,name, MAX(created_at) AS latest_created_at, next_run_time  FROM jobs_recordManager GROUP BY agent, name, next_run_time  ORDER BY latest_created_at DESC LIMIT {str(n)}")

        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        results = []
        for row in rows:
            record = dict(zip(columns, row))
            # Convert latest_created_at to human-readable IST format
            record['latest_created_at'] = self.format_epoch_to_ist(record['latest_created_at'])
            # Optionally, format next_run_time if needed
            record['next_run_time'] = self.format_next_run_time(record['next_run_time'])
            results.append(record)

        json_result = json.dumps(results, default=str)  # Use default=str to handle any non-serializable data

        # Close the connection
        self.conn.close()

        return json_result
    
    def fetch_nodes_as_json(self,n=10):
        cursor =self.conn.cursor()
        #cursor.execute(f"SELECT agent,name, MAX(created_at) AS latest_created_at, next_run_time  FROM jobs_recordManager GROUP BY agent, name, next_run_time  ORDER BY latest_created_at DESC LIMIT {str(n)}")
        cursor.execute(f"SELECT DISTINCT idx,agent FROM jobs_recordManager ")

        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        results = []
        for row in rows:
            record = dict(zip(columns, row))
            # # Convert latest_created_at to human-readable IST format
            # record['latest_created_at'] = self.format_epoch_to_ist(record['latest_created_at'])
            # # Optionally, format next_run_time if needed
            # record['next_run_time'] = self.format_next_run_time(record['next_run_time'])
            results.append(record)

        json_result = json.dumps(results, default=str)  # Use default=str to handle any non-serializable data

        # Close the connection
        self.conn.close()

        return json_result
    
    def close(self):
        self.conn.close()

    
    def get_data_bkp_file(self, source_db=None,target_location=None,target_file_name=None): ## my.db ,"D:\\bkuplocaion","mybkp.file"
        import sqlite3
        import time
        import shutil
        import tempfile
        import os
        
        unix_timestamp = time.time()



        #A tmp file should be used here that can be deleted automatically (library feature)
        print(f"data of source db {source_db}")
        for source in source_db:
            # unix_timestamp = time.time()
            print(source)
            if os.path.exists(source):
                if source.endswith('.db'):
                    # source = r"D:\3hs-working-kk\flask\ab server\FlaskWebProject3_25.8.5.1_05082025_184\FlaskWebProject3\FlaskWebProject3\7c3eb001aa90c597e790f0468db1e0416a89089266e5d1dbc018bac5aa8a306a"

                    t_working_file = f"{source}_{unix_timestamp}.kdb"
                    # with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix=".kd") as d:
                    #     t_working_file = f"{d.name}"
                    #     d.close()

                    d = tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix=".kd")
                    t_working_file = f"{d.name}"
                    d.close()

                    try:
                        print(f"==============={t_working_file}======={source}========")
                        # t_working_file = f"{d.name}"
                        # source_conn = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
                        source_conn = sqlite3.connect(f"file:./{source}?mode=ro", uri=True)
                        dest_conn = sqlite3.connect(t_working_file)
                        source_conn.backup(dest_conn,pages=500)
                        dest_conn.close()
                        source_conn.close()

                        #compression goes here
                        # target_file_compress = gzip.GzipFile(t_working_file)
                        #compressed_file = f"{t_working_file}.kdb"
                        compressed_file = f"{source}_{unix_timestamp}.kdb"
                        with open(t_working_file, 'rb') as f_in:
                            with gzip.open(compressed_file, 'wb',) as f_out:
                                shutil.copyfileobj(f_in, f_out)
                                f_out.close()  ##forcefully try to close
                            f_in.close()    ##forcefully try to close
                        # after compression done return file path toupload
                
                        directory_path = "backup_dir"
                        if not os.path.exists(directory_path):
                            os.makedirs(directory_path)
                        shutil.move(compressed_file, directory_path)
                        try:
                            os.remove(t_working_file)
                        except Exception as e:
                            print(f"Error on delete file {str(e)}")

                    except sqlite3.Error as e:
                        print(f"Backup failed for {source}: {e}")
                        try:
                            os.remove(t_working_file)
                        except Exception as e:
                            print(f"Error on delete file {str(e)}")
                else:
                    compressed_file = f"{source}_{unix_timestamp}.kdb"
                    with open(source, 'rb') as f_in:
                            with gzip.open(compressed_file, 'wb',) as f_out:
                                shutil.copyfileobj(f_in, f_out)
                                f_out.close()  ##forcefully try to close
                            f_in.close()    ##forcefully try to close
                    directory_path = "backup_dir"
                    if not os.path.exists(directory_path):
                        os.makedirs(directory_path)
                    shutil.move(compressed_file, directory_path)
        

        return True


