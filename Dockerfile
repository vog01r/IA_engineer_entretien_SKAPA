# Image Python officielle légère (slim = pas de build tools, ~150 MB)
FROM python:3.12-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier uniquement requirements d'abord (cache Docker = pas de re-install si code change)
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app/ app/
COPY main.py .

# Port exposé (convention FastAPI)
EXPOSE 8000

# Créer les tables au démarrage, puis lancer uvicorn (sans reload en prod)
# PORT injecté par Railway au runtime
CMD ["sh", "-c", "python -c \"from app.db.crud import create_tables; create_tables()\" && uvicorn app.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
