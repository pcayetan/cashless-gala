# -*- coding:utf-8 -*
import logging

logging.basicConfig(level=logging.INFO)

from . import settings

from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///%s" % settings.DB_PATH, convert_unicode=True)
db: Session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Model = declarative_base()
Model.query = db.query_property()
