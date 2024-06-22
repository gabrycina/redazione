import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()