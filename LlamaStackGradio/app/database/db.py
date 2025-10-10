# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    from client import DATABASE_URL
except ImportError:
    from ..client import DATABASE_URL

engine = create_engine(DATABASE_URL,
                        connect_args={"check_same_thread": False}# Necesario para SQLite
                    )  

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
