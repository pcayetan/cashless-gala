# -*- coding:utf-8 -*
import sys

DB_PATH = "database.sqlite"

try:
    from .settings_custom import *

    print("Custom settings imported", file=sys.stderr)
except:
    print("Custom settings failed", file=sys.stderr)
