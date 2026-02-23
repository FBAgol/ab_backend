from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from dotenv import load_dotenv
import os

load_dotenv()

# Verwende den asynchronen Treiber aiomysql
MYSQL_USER = os.getenv("MYSQL_USER", "appuser")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "apppassword")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "abschlussprojekt")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{DB_HOST}:{DB_PORT}/{MYSQL_DATABASE}"
)

# Erstelle die asynchrone Engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Erstelle eine asynchrone Session
session_local = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Definiere die Basisklasse für Modelle
class Base(DeclarativeBase, MappedAsDataclass):
    pass

# Dependency für FastAPI
async def get_db():
    db = session_local()
    try:
        yield db
    finally:
        await db.close()
