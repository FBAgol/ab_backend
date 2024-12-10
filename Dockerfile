# Verwende Python 3.12 slim als Basis
FROM python:3.12-slim

# Setze Umgebungsvariablen für Poetry
ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/root/.local/bin:$PATH"

# Installiere Poetry und System-Abhängigkeiten
RUN apt-get update && \ 
    apt-get install -y curl gcc g++ make libffi-dev libgl1 libglib2.0-0 && \ 
    apt-get clean && \ 
    curl -sSL https://install.python-poetry.org | python3

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere den gesamten Code ins Arbeitsverzeichnis
COPY . /app


# Installiere alle Abhängigkeiten mit Poetry
RUN poetry install
 

ENV PATH="/app/.venv/bin:$PATH"
#CMD ["nc", "-l", "5500"] netcat-openbsd 

# Exponiere den Port 8081 für das Backend
EXPOSE 8081

# Verwende Poetry, um uvicorn auszuführen
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
