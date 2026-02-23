from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Definiamo il percorso del database.
# Creerà un file 'portfolio.db' nella cartella 'data' che abbiamo montato in Docker.
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DB_DIR, exist_ok=True) # Assicuriamoci che la cartella esista

SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'portfolio.db')}"

# connect_args={"check_same_thread": False} è necessario solo per SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency per FastAPI: apre una sessione al DB per ogni richiesta e la chiude alla fine
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()