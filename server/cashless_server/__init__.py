# -*- coding:utf-8 -*
import logging
import functools

logging.basicConfig(level=logging.INFO)

from . import settings

from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

_engine = None
_db = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{settings.DB_PATH}")
    return _engine


def get_db() -> scoped_session:
    global _db
    if _db is None:
        _db = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
        )
    return _db


def db_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db = get_db()
        session: Session = db()
        ret = func(*args, session, **kwargs)
        db.remove()
        return ret

    return wrapper
