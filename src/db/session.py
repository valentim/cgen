from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import Settings

DATABASE_URL = Settings().DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
