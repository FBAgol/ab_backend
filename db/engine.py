from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

# Verwende den asynchronen Treiber aiomysql
SQLALCHEMY_DATABASE_URL = (
    "mysql+aiomysql://appuser:apppassword@db:3306/abschlussprojekt"
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
