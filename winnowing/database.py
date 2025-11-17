# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "postgresql://postgres:19052004@localhost:5432/checkdoc"

engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=30, pool_timeout=60, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)