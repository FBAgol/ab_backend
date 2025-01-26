from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
import socketio
import logging
import os
from uuid import UUID
import sqlalchemy as sa
from fastapi.openapi.utils import get_openapi
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import Base, engine
from db.models import Telekom_Editor    
from cors_config import add_cors_middleware
from routers import superadmin_router, companyeditor_router, telekomeditor_router
from jwt_utils import get_user_id_from_token

app = FastAPI()

# CORS-Konfiguration anwenden
add_cors_middleware(app)

# WebSocket-Server erstellen
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])
socket_app = socketio.ASGIApp(sio, app)

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
       # logger.info("Datenbanktabellen wurden initialisiert.")
    images_directory = "images"
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)
        logger.info(f"Ordner '{images_directory}' wurde erstellt.")
    else:
        logger.info(f"Ordner '{images_directory}' existiert bereits.")

# Binden des zentralen Routers an die Hauptanwendung
app.include_router(main_router, prefix="/api/v1")

# Deine bestehenden Router-Registrierungen und Logik
# z. B. app.include_router(companyeditor_router)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    # Bearer Token Security
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Sicherheit auf alle Endpunkte anwenden
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method.lower() in ["get", "post", "put", "delete"]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
# WebSocket-Events
@sio.event
async def connect(sid, environ, auth=None):
    print(f"Client connected: {sid}")
    token = environ.get('HTTP_AUTHORIZATION')  # Extrahiere das Token aus dem Header

    if auth and 'token' in auth:
        token = auth['token']
        try:
            editor_id = UUID(get_user_id_from_token(token))  # Extrahiere die editor_id aus dem Token
            query = sa.select(Telekom_Editor).where(Telekom_Editor.id == editor_id)
            async with AsyncSession(engine) as session:
                result = await session.execute(query)
                editor = result.scalar_one_or_none()

            if editor:
                print(f"User {editor_id} connected")
                await sio.save_session(sid, {'editor_id': str(editor_id)})
                await sio.enter_room(sid, str(editor_id))  # Editor-ID als Room-ID nutzen
                await sio.emit('notification', {'msg': 'Connected to notifications'}, to=sid)
            else:
                print(f"Editor mit ID {editor_id} wurde nicht gefunden.")
        except Exception as e:
            print(f"Error extracting editor_id from token: {e}")
    else:
        print("No token provided")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    session = await sio.get_session(sid)
    if session.get('editor_id'):
        await sio.leave_room(sid, session['editor_id'])

# Hauptanwendung
app.mount("/", socket_app)  # WebSocket-App mounten