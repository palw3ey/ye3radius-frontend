# Basis-Image
FROM python:3.9-alpine

# Arbeitsverzeichnis im Container
WORKDIR /app

# Abhängigkeiten installieren
RUN apk add --no-cache mariadb-dev gcc musl-dev libffi-dev

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungsdateien kopieren
COPY . .

# Port freigeben
EXPOSE 5000

# Startbefehl
CMD ["python", "app.py"]
