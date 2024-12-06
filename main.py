from fastapi import FastAPI
from db.engine import Base, engine

from routers.routers import router


app = FastAPI()


@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(router)
