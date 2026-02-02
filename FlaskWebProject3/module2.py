from msilib import Table
import os
from six import b
from sqlalchemy import create_engine, Column, Integer, String, JSON, FLOAT,INTEGER, table,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, sessionmaker
from flask import Blueprint, request, jsonify
from datetime import datetime

# Import models - use MSSQL models when USE_MSSQL, else legacy SQLite models
try:
    from FlaskWebProject3.db_config import USE_MSSQL
except ImportError:
    USE_MSSQL = False

if USE_MSSQL:
    from FlaskWebProject3.models import (
        Base,
        BackupLogs,
        BackupMain,
        RestoreChild,
        RestoreParent,
        NodeJob,
    )
    restore_child = RestoreChild
    restore_parent = RestoreParent
else:
    _Base = declarative_base()
    Base = _Base

    class BackupLogs(_Base):
        __tablename__ = "backups"
        id = Column(FLOAT, primary_key=True)
        name = Column(FLOAT)
        date_time = Column(FLOAT)
        from_computer = Column(String)
        from_path = Column(String)
        data_repo = Column(String)
        mime_type = Column(String)
        size = Column(FLOAT)
        file_name = Column(String)
        full_file_name = Column(String)
        log = Column(JSON)
        pNameText = Column(String)
        pIdText = Column(String)
        bkupType = Column(String)
        sum_all = Column(INTEGER)
        sum_done = Column(INTEGER)
        done_all = Column(INTEGER)
        mode = Column(String)
        status = Column(String)
        data_repod = Column(String)
        repid = Column(String)
        fidi = Column(String)

    class BackupMain(_Base):
        __tablename__ = "backups_M"
        id = Column(FLOAT, primary_key=True)
        date_time = Column(FLOAT)
        from_computer = Column(String)
        from_path = Column(String)
        data_repo = Column(String)
        mime_type = Column(String)
        file_name = Column(String)
        size = Column(FLOAT)
        pNameText = Column(String)
        pIdText = Column(String)
        bkupType = Column(String)
        sum_all = Column(INTEGER)
        sum_done = Column(INTEGER)
        done_all = Column(INTEGER)
        mode = Column(String)
        status = Column(String)
        data_repod = Column(String)

    class RestoreChild(_Base):
        __tablename__ = "restores"
        id = Column(Integer, primary_key=True, autoincrement=True)
        RestoreLocation = Column(String(255), nullable=False)
        backup_id = Column(FLOAT, nullable=False)
        backup_file_id = Column(FLOAT, nullable=False)
        backup_name = Column(String(255), nullable=False)
        file = Column(String(255), nullable=False)
        file_restore_time = Column(FLOAT, nullable=False)
        file_start = Column(String(255), nullable=False)
        file_end = Column(String(255), nullable=False)
        from_backup_pc = Column(String(255), nullable=False)
        reason = Column(String(255), nullable=False)
        restore = Column(String(255), nullable=False)
        storage_type = Column(String(255), nullable=False)
        p_id = Column(Float, nullable=True)
        t14 = Column(FLOAT, nullable=False)
        targetlocation = Column(String(255), nullable=False)
        torestore_pc = Column(String(255), nullable=False)

    class RestoreParent(_Base):
        __tablename__ = "restoreM"
        id = Column(Integer, primary_key=True, autoincrement=True)
        RestoreLocation = Column(String(255), nullable=False)
        backup_id = Column(FLOAT, nullable=False)
        storage_type = Column(String(255), nullable=False)
        backup_name = Column(String(255), nullable=False)
        p_id = Column(Float, nullable=True)
        t14 = Column(FLOAT, nullable=False)
        from_backup_pc = Column(String(255), nullable=False)
        targetlocation = Column(String(255), nullable=False)
        torestore_pc = Column(String(255), nullable=False)

    class NodeJob(_Base):
        __tablename__ = "node_jobs"
        id = Column(Integer, primary_key=True, autoincrement=True)
        node = Column(String, nullable=False, unique=True)
        nodeName = Column(String, nullable=True)
        total_success = Column(Integer, default=0)
        total_failed = Column(Integer, default=0)
        data = Column(JSON, nullable=True)
        failed_data = Column(JSON, nullable=True)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    restore_child = RestoreChild
    restore_parent = RestoreParent


def create_database(database_name):
    """
    Ensure database tables exist (idempotent).
    For MSSQL (USE_MSSQL=1): creates all tables via SQLAlchemy.
    For SQLite (USE_MSSQL=0): uses execute_queries_sqlite (legacy) to create tables in the given path.
    """
    try:
        from FlaskWebProject3.db_config import USE_MSSQL
        if USE_MSSQL:
            from FlaskWebProject3.db import create_all_tables
            create_all_tables()
            return True
        else:
            from FlaskWebProject3.sqlite_legacy import execute_queries_sqlite
            db_query_pairs = [
                (f"{database_name}", [
                    "CREATE TABLE IF NOT EXISTS backups_M (id FLOAT NOT NULL,date_time FLOAT,from_computer VARCHAR,from_path VARCHAR, data_repo VARCHAR,mime_type VARCHAR, file_name VARCHAR,size FLOAT, pNameText VARCHAR,pIdText VARCHAR, bkupType VARCHAR, PRIMARY KEY (id))",
                    "CREATE TABLE IF NOT EXISTS backups (id FLOAT NOT NULL, name FLOAT, date_time FLOAT, from_computer VARCHAR, from_path VARCHAR, data_repo VARCHAR, mime_type VARCHAR, size FLOAT, file_name VARCHAR, full_file_name VARCHAR, log JSON, pNameText VARCHAR, pIdText VARCHAR, bkupType VARCHAR, PRIMARY KEY (id))",
                    "ALTER TABLE backups_M ADD sum_all INTEGER",
                    "ALTER TABLE backups_M ADD sum_done INTEGER",
                    "ALTER TABLE backups_M ADD done_all INTEGER",
                    "ALTER TABLE backups_M ADD status VARCHAR",
                    "ALTER TABLE backups_M ADD mode VARCHAR",
                    "ALTER TABLE backups_M ADD data_repod VARCHAR",
                    "ALTER TABLE backups_M ADD repid VARCHAR",
                    "ALTER TABLE backups ADD sum_all INTEGER",
                    "ALTER TABLE backups ADD sum_done INTEGER",
                    "ALTER TABLE backups ADD done_all INTEGER",
                    "ALTER TABLE backups ADD status VARCHAR",
                    "ALTER TABLE backups ADD mode VARCHAR",
                    "ALTER TABLE backups ADD data_repod VARCHAR",
                    "ALTER TABLE backups ADD repid VARCHAR",
                    "ALTER TABLE backups ADD fidi VARCHAR",
                    "CREATE TABLE IF NOT EXISTS restores (id INTEGER NOT NULL, RestoreLocation VARCHAR(255) NOT NULL, backup_id FLOAT NOT NULL, backup_file_id FLOAT NOT NULL, backup_name VARCHAR(255) NOT NULL, file VARCHAR(255) NOT NULL, file_restore_time FLOAT NOT NULL, file_start DATETIME NOT NULL, file_end DATETIME NOT NULL, from_backup_pc VARCHAR(255) NOT NULL, reason VARCHAR(255) NOT NULL, restore VARCHAR(255) NOT NULL, storage_type VARCHAR(255) NOT NULL, t14 FLOAT NOT NULL, targetlocation VARCHAR(255) NOT NULL,torestore_pc VARCHAR(255) NOT NULL,p_id FLOAT NOT NULL, PRIMARY KEY (id))",
                    "CREATE TABLE IF NOT EXISTS restoreM (id INTEGER NOT NULL, RestoreLocation VARCHAR(255) NOT NULL, backup_id FLOAT NOT NULL, storage_type VARCHAR(255) NOT NULL, backup_name VARCHAR(255) NOT NULL, t14 FLOAT NOT NULL, from_backup_pc VARCHAR(255) NOT NULL, targetlocation VARCHAR(255) NOT NULL, torestore_pc VARCHAR(255) NOT NULL,p_id FLOAT NOT NULL, PRIMARY KEY (id))",
                    "ALTER TABLE restores ADD p_id FLOAT NULL",
                    "ALTER TABLE restoreM ADD p_id FLOAT NULL",
                ])
            ]
            execute_queries_sqlite(db_query_pairs)
            return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False


database_blueprint = Blueprint("database", __name__)


@database_blueprint.route("/create_database", methods=["POST"])
def create_database_route():
    from FlaskWebProject3 import app
    data = request.get_json()
    database_name = data.get("database_name")
    database_name = str(database_name).replace("{{PATH}}", app.config["location"])
    if not database_name:
        return jsonify({"message": "Database name is required"}), 400
    parent_dir = os.path.dirname(database_name)
    if parent_dir:
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except OSError:
            pass

    try:
        if create_database(database_name):
            return (
                jsonify(
                    {"message": f'Database "{database_name}" created successfully'}
                ),
                201,
            )
        else:
            return (
                jsonify({"message": f'Database "{database_name}" already exists'}),
                200,
            )

        # from sqlalchemy import Table,Column
        # table = Table(BackupMain().__tablename__)

    except Exception as e:
        return jsonify({"message": f"Error creating database: {str(e)}"}), 500


@database_blueprint.route("/restore", methods=["POST"])
def get_restore_data():
    from time import time

    selectedStorageType = request.json.get("selectedStorageType", "")
    selectedAgent = request.json.get("selectedAgent", "")
    startDate = request.json.get("startDate", time() - time())
    endDate = request.json.get("selectedStorageType", time())