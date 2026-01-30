import datetime

from flask import app
from fClient.fingerprint import getCode
from runserver import Base



from sqlalchemy import create_engine


#engine = create_engine("sqlite:///"+getCode())
engine = create_engine("sqlite:///"+ str(app.config.get("getCode",None)))
Base.metadata.create_all(engine)