# Utilise une image officielle Python comme base
FROM python:3.11-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie les fichiers de dépendances
COPY requirements.txt ./

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code source dans le conteneur
COPY . .

# Expose le port utilisé par Django (par défaut 8000)
EXPOSE 8000

# Commande de démarrage du serveur de développement Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Explications :
# - FROM : Choisit l'image de base (ici Python 3.11 allégée)
# - WORKDIR : Définit le dossier de travail
# - COPY requirements.txt : Copie d'abord les dépendances pour optimiser le cache Docker
# - RUN pip install : Installe les dépendances
# - COPY . . : Copie tout le code du projet
# - EXPOSE : Ouvre le port 8000
# - CMD : Lance le serveur Django
