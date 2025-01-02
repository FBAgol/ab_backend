from fastapi import FastAPI, APIRouter
from db.engine import Base, engine

from routers import superadmin_router, companyeditor_router

app = FastAPI()

# Erstellen eines zentralen Routers
main_router = APIRouter()

# Hinzufügen der spezifischen Router zum zentralen Router
main_router.include_router(superadmin_router, prefix="/superadmin", tags=["superadmin"])
main_router.include_router(companyeditor_router, prefix="/companyeditor", tags=["companyeditor"])

@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Binden des zentralen Routers an die Hauptanwendung
app.include_router(main_router)
