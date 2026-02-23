# Backend App

## Technologie-Stack
- **FastAPI** – Web Framework
- **SQLAlchemy** (async) – ORM
- **MySQL 8.0** – Datenbank
- **aiomysql** – Async MySQL Treiber
- **python-socketio** – WebSocket / Echtzeit-Kommunikation
- **PyJWT** – JWT Authentifizierung
- **Passlib / bcrypt** – Passwort-Hashing
- **Ultralytics YOLOv8** – KI-Bildanalyse
- **Poetry** – Dependency Manager
- **Docker + Docker Compose** – Containerisierung

---

## Voraussetzungen
- Python 3.12+
- Poetry
- Docker Desktop

---

## Umgebungsvariablen (.env)

Erstelle eine `.env` Datei im Projektroot mit folgenden Variablen:

```env
# Datenbank
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=abschlussprojekt
MYSQL_USER=appuser
MYSQL_PASSWORD=apppassword
DB_HOST=db
DB_PORT=3306

# JWT
SECRET_KEY=dein_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7

# E-Mail
EMAIL_PASSWORD=dein_email_passwort
```

---

## Starten mit Docker Compose (empfohlen)

Startet automatisch **MySQL** und das **FastAPI Backend** zusammen:

```bash
# Zum ersten Mal oder nach Änderungen
docker compose up --build

# Im Hintergrund
docker compose up --build -d

# Stoppen
docker compose down

# Stoppen + Datenbank löschen
docker compose down -v
```

> Die Datenbanktabellen werden beim ersten Start **automatisch erstellt**.

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| MySQL | localhost:3306 |

---

## Lokale Entwicklung (ohne Docker)

1. Abhängigkeiten installieren:
```bash
poetry install
```

2. In `db/engine.py` den `DB_HOST` in der `.env` von `db` auf `localhost` ändern:
```env
DB_HOST=localhost
```

3. Server starten:
```bash
poetry run uvicorn main:app --reload
```

---

## Projektstruktur

```
ab_backend/
├── main.py                  # FastAPI App, WebSocket Events
├── docker-compose.yml       # Docker Compose (Backend + MySQL)
├── Dockerfile               # Docker Image für Backend
├── .env                     # Umgebungsvariablen (nicht ins Git!)
├── pyproject.toml           # Poetry Abhängigkeiten
├── db/
│   ├── engine.py            # DB-Verbindung (liest aus .env)
│   ├── models.py            # SQLAlchemy Modelle
│   └── hash_password.py     # Passwort-Hashing
├── routers/                 # FastAPI Router
├── operations/              # Business-Logik
├── schemas/                 # Pydantic Input-Schemas
├── jwt_utils/               # JWT Token Erstellung & Validierung
├── NT_O_Detection_v3_800/   # YOLOv8 Bildanalyse
└── images/                  # Gespeicherte Bilder (original + analysiert)
```

---

## API Endpunkte (Übersicht)

Alle Endpunkte sind unter `/api/v1/` erreichbar und benötigen einen **Bearer Token** (außer Login/Register).

| Prefix | Beschreibung |
|---|---|
| `/api/v1/superadmin` | SuperAdmin Verwaltung |
| `/api/v1/companyeditor` | Company Editor Operationen |
| `/api/v1/telekomeditor` | Telekom Editor Operationen |
| `/api/v1/email` | E-Mail versenden |

Vollständige Dokumentation: **http://localhost:8000/docs**

---

## API Dokumentation (Swagger)

FastAPI generiert automatisch eine interaktive API-Dokumentation:

| Tool | URL | Beschreibung |
|---|---|---|
| **Swagger UI** | http://localhost:8000/docs | Interaktiv – Endpunkte direkt testen |
| **ReDoc** | http://localhost:8000/redoc | Übersichtliche Dokumentation |
| **OpenAPI JSON** | http://localhost:8000/openapi.json | Rohes OpenAPI Schema |

> Alle Endpunkte sind mit **Bearer Token** (JWT) gesichert.
> In der Swagger UI oben rechts auf **Authorize** klicken und den Token eingeben.

