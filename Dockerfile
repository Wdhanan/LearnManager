# Basis-Image
FROM python:3.9-slim

# Arbeitsverzeichnis
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendung kopieren
COPY . .

# Umgebungsvariablen setzen
ENV STREAMLIT_SERVER_PORT=8501

# Port freigeben
EXPOSE 8501

# Startbefehl
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]