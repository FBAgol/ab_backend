from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
import pymysql
pymysql.install_as_MySQLdb()

SQLALCHEMY_DATABASE_URL = (
    "mysql+pymysql://appuser:apppassword@db:3306/abschlussprojekt"
)


engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

session_local = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


async def get_db():
    db = session_local()
    try:
        yield db
    finally:
        await db.close()
