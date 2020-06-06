# -*- coding:utf-8 -*
from . import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///%s" % settings.DB_PATH, convert_unicode=True)
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Model = declarative_base()
Model.query = db.query_property()
