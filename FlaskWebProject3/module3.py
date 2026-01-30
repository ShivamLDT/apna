import os
from sqlalchemy import create_engine, Column, Integer, String, JSON,FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Blueprint, request, jsonify

# Define the base class for declarative models
Base = declarative_base()


# Define your SQLAlchemy model
class BackupLogs(Base):
    __tablename__ = "backups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date_time = Column(FLOAT)
    from_computer = Column(String)
    from_path = Column(String)
    data_repo = Column(String)
    log = Column(JSON)


def create_database(database_name):

    # Check if the database file exists
    if not os.path.exists(f"{database_name}.db"):
        # Define the SQLAlchemy engine for the specified database
        engine = create_engine(f"sqlite:///{database_name}.db")
        # Create the tables in the database
        Base.metadata.create_all(engine)
        return True
    else:
        return False

database_blueprint = Blueprint("database", __name__)

@database_blueprint.route("/create_database", methods=["POST"])
def create_database_route():
    data = request.get_json()
    database_name = data.get("database_name")

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
    except Exception as e:
        return jsonify({"message": f"Error creating database: {str(e)}"}), 500

 