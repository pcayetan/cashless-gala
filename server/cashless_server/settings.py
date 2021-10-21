# -*- coding:utf-8 -*
import logging
import os

DB_PATH = "database.sqlite"

try:
    with open(os.environ.get("CFG", "settings_custom.py"), "r") as f:
        exec(f.read())

    logging.info("Custom settings imported")
except Exception as e:
    logging.warning(f"Custom settings failed: {e}")
