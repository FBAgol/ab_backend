import jwt
from datetime import datetime, timedelta, timezone  # Importiere 'timezone'
from typing import Optional
from fastapi import HTTPException, status
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS


# Hilfsfunktion: Erstelle das Access-Token mit 1 Tag Ablaufzeit
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()  # Daten aus dem Payload kopieren
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta  # Korrigierte Zeile
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)  # Ablaufzeit auf 1 Tag setzen
    to_encode.update({"exp": expire})  # Ablaufzeit im Payload hinzufügen
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Token kodieren
    return encoded_jwt

# Hilfsfunktion: Erstelle das Refresh-Token mit einer Standard-Ablaufzeit von 7 Tagen
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta  # Korrigierte Zeile
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(days=7)  # Ablaufzeit für Refresh-Token: 7 Tage
    to_encode.update({"exp": expire})  # Ablaufzeit im Payload hinzufügen
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Token kodieren
    return encoded_jwt

# Hilfsfunktion: Verifiziere das Token
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Token dekodieren und verifizieren
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")

# Extrahiere die Benutzer-ID aus dem Token
def get_user_id_from_token(token: str) -> str:
    payload = verify_token(token)
    return payload.get("sub")  # 'sub' enthält die Benutzer-ID
