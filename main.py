from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
import logging
import os

from db.engine import Base, engine
from cors_config import add_cors_middleware
from routers import superadmin_router, companyeditor_router, telekomeditor_router

app = FastAPI()

# CORS-Konfiguration anwenden
add_cors_middleware(app)


app.mount("/images", StaticFiles(directory="images"), name="images")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Erstellen eines zentralen Routers
main_router = APIRouter()

# Hinzufügen der spezifischen Router zum zentralen Router
main_router.include_router(superadmin_router, prefix="/superadmin", tags=["superadmin"])
main_router.include_router(companyeditor_router, prefix="/companyeditor", tags=["companyeditor"])
main_router.include_router(telekomeditor_router, prefix="/telekomeditor", tags=["telekomeditor"])

@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Datenbanktabellen wurden initialisiert.")
    images_directory = "images"
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)
        logger.info(f"Ordner '{images_directory}' wurde erstellt.")
    else:
        logger.info(f"Ordner '{images_directory}' existiert bereits.")

# Binden des zentralen Routers an die Hauptanwendung
app.include_router(main_router, prefix="/api/v1")

