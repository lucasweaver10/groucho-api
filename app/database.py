from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

# Configure engine with PostgreSQL-specific settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Helps with connection drops
    pool_recycle=300,    # Recycle connections every 5 minutes
)

def get_db():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
