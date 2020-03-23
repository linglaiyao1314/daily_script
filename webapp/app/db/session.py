from sqlalchemy import create_engine,MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from app.core import config

engine = create_engine(config.APP_SETTINGS.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData(engine)
metadata.create_all()