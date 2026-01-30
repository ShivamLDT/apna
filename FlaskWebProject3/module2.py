from msilib import Table
import os
from six import b
from sqlalchemy import create_engine, Column, Integer, String, JSON, FLOAT,INTEGER, table,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, sessionmaker
from flask import Blueprint, request, jsonify
from datetime import datetime
# Define the base class for declarative models
Base = declarative_base()


# Define your SQLAlchemy model

class restore_child(Base):
    from sqlalchemy import create_engine, Column, Integer, String, DateTime,Float
    from sqlalchemy.ext.declarative import declarative_base

    __tablename__ = "restores"

    id = Column(Integer, primary_key=True,autoincrement=True)
    RestoreLocation = Column(String(255), nullable=False)
    backup_id = Column(Float(255), nullable=False)
    backup_file_id = Column(Float(255), nullable=False)
    backup_name = Column(String(255), nullable=False)
    file = Column(String(255), nullable=False)
    file_restore_time = Column(Float(255), nullable=False)
    file_start = Column(String(255), nullable=False)
    file_end = Column(String(255), nullable=False)
    from_backup_pc = Column(String(255), nullable=False)
    reason = Column(String(255), nullable=False)
    restore = Column(String(255), nullable=False)
    storage_type = Column(String(255), nullable=False)
    p_id = Column(Float, nullable=True)
    t14 = Column(Float(255), nullable=False)
    targetlocation = Column(String(255), nullable=False)
    torestore_pc = Column(String(255), nullable=False)
    
    @classmethod
    def to_dict(cls, instance):
        """ Helper function to convert model instances to dictionary. """
        return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}

    def __repr__(self):
        return f"<FileRecord {self.file}, {self.fileurl}>"
    
#class restore_parent(db.Model):
class restore_parent(Base):
    from sqlalchemy import create_engine, Column, Integer, String, DateTime,Float
    from sqlalchemy.ext.declarative import declarative_base

    __tablename__ = "restoreM"

    id = Column(Integer, primary_key=True,autoincrement=True)
    RestoreLocation = Column(String(255), nullable=False)
    backup_id = Column(Float(255), nullable=False)
    storage_type = Column(String(255), nullable=False)
    backup_name = Column(String(255), nullable=False)
    p_id = Column(Float(255))
    t14 = Column(Float(255), nullable=False)
    from_backup_pc = Column(String(255), nullable=False)
    targetlocation = Column(String(255), nullable=False)
    torestore_pc = Column(String(255), nullable=False)

    @classmethod
    def to_dict(cls, instance,bwith_children=False,session=None):
        """ Helper function to convert model instances to dictionary. """
        parent_dict = {column.name: getattr(instance, column.name) for column in instance.__table__.columns}
        if not bwith_children or not session:
            return parent_dict
        else:
            
            x= session.query(restore_child).filter_by(backup_id=parent_dict.get("backup_id"),t14=parent_dict.get("t14"))
            parent_dict.update({"restore_files":[restore_child.to_dict(fx) for fx in x]})

        return parent_dict

            

    @classmethod
    def getchildren_dict(cls, instance):
        """ Helper function to convert model instances to dictionary. """
        return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}

        
        
    
class BackupLogs(Base):
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


class BackupMain(Base):
    __tablename__ = "backups_M"

    # id = Column(FLOAT, primary_key=True)
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

class NodeJob(Base):
    __tablename__ = "node_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node = Column(String, nullable=False, unique=True) 
    nodeName = Column(String, nullable=True)
    total_success = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def create_database(database_name):
    b = True
    # # Check if the database file exists
    # if not os.path.exists(f"{database_name}.db"):
    #     # Define the SQLAlchemy engine for the specified database
    #     engine = create_engine(f"sqlite:///{database_name}.db")
    #     # Create the tables in the database
    #     Base.metadata.create_all(engine)

    # else:
    #     b = False
    # try:
    #     import sqlalchemy
    #     engine = create_engine(f"sqlite:///{database_name}.db",)
    #     if sqlalchemy.inspect(engine).has_table("backups"):
    #         #modify table code
    #     else:
    #         engine.ex

    #     if sqlalchemy.inspect(engine).has_table("backups_M"):

    # except:
    #     pass
    ######################################################################
    # import sqlite3

    # #if not os.path.exists(f"{database_name}"):
    # try:
    #     # Connect to a database (or create it if it doesn't exist)
    #     conn = sqlite3.connect(f"{database_name}")
    #     print("Database connection established.")
    #     if b:

    #         try:
    #             # Connect to the database
    #             # conn = sqlite3.connect(f"{database_name}")
    #             cur = conn.cursor()

    #             # Create a table
    #             cur.execute(
    #                 "CREATE TABLE IF NOT EXISTS backups_M (id FLOAT NOT NULL,date_time FLOAT,from_computer VARCHAR,from_path VARCHAR, data_repo VARCHAR,mime_type VARCHAR, file_name VARCHAR,size FLOAT, pNameText VARCHAR,pIdText VARCHAR, bkupType VARCHAR, PRIMARY KEY (id))"
    #             )

    #             # Commit the changes and close the connection
    #             # conn.commit()
    #             b = True
    #             cur.close()
    #         except sqlite3.Error as e:
    #             print(f"Error connecting to database: {e}")
    #             b = False

    #     if b:
    #         try:
    #             # Connect to the database
    #             cur1 = conn.cursor()
    #             # Create a table
    #             cur1.execute(
    #                 "CREATE TABLE  IF NOT EXISTS backups (id FLOAT NOT NULL, name FLOAT, date_time FLOAT, from_computer VARCHAR, from_path VARCHAR, data_repo VARCHAR, mime_type VARCHAR, size FLOAT, file_name VARCHAR, full_file_name VARCHAR, log JSON, pNameText VARCHAR, pIdText VARCHAR, bkupType VARCHAR, PRIMARY KEY (id))"
    #             )

    #             # Commit the changes and close the connection
    #             conn.commit()
    #             b = True
    #         except sqlite3.Error as e:
    #             print(f"Error connecting to database: {e}")
    #             b = False

    # except sqlite3.Error as e:
    #     print(f"Error connecting to database: {e}")
    #     b = False
    # finally:
    #     if conn:
    #         conn.close()
    #         print("Database connection closed.")
    #     if cur:
    #         cur.close()
    # #if not b:
    #     #os.remove(f"{database_name}")
    # return b

    from sqlite_managerA import SQLiteManager
    sqlite_manager = SQLiteManager()
    # Define the database paths and queries
    db_query_pairs = [
        (
            f"{database_name}",
            [
                "CREATE TABLE IF NOT EXISTS backups_M (id FLOAT NOT NULL,date_time FLOAT,from_computer VARCHAR,from_path VARCHAR, data_repo VARCHAR,mime_type VARCHAR, file_name VARCHAR,size FLOAT, pNameText VARCHAR,pIdText VARCHAR, bkupType VARCHAR, PRIMARY KEY (id))",
                "CREATE TABLE  IF NOT EXISTS backups (id FLOAT NOT NULL, name FLOAT, date_time FLOAT, from_computer VARCHAR, from_path VARCHAR, data_repo VARCHAR, mime_type VARCHAR, size FLOAT, file_name VARCHAR, full_file_name VARCHAR, log JSON, pNameText VARCHAR, pIdText VARCHAR, bkupType VARCHAR, PRIMARY KEY (id))",
                
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
                
                 "ALTER TABLE resotres ADD p_id FLOAT NULL",
                 "ALTER TABLE resotreM ADD p_id FLOAT NULL",
            ],
        )
    ]
    
    results = sqlite_manager.execute_queries(db_query_pairs)


database_blueprint = Blueprint("database", __name__)


@database_blueprint.route("/create_database", methods=["POST"])
def create_database_route():
    from FlaskWebProject3 import app
    data = request.get_json()
    database_name = data.get("database_name")
    database_name = str(database_name).replace("{{PATH}}", app.config["location"])
    if not database_name:
        return jsonify({"message": "Database name is required"}), 400

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