# Verset de l'année — Déploiement

Ce dépôt contient une petite application Flask pour tirer un verset biblique. Ci‑dessous les instructions essentielles pour lancer et déployer.

## Prérequis
- Docker & Docker Compose
- (ou Python 3.11 + venv)

## Variables d'environnement
Définissez `SECRET_KEY` (chaîne longue & aléatoire) avant de démarrer en production.
Copiez `.env.example` en `.env` pour usage local.

## Exécuter localement avec Docker Compose
1. Copier l'exemple d'environnement:
```bash
cp .env.example .env
# modifier .env pour définir SECRET_KEY
```
2. Build et lancement:
```bash
docker-compose build
docker-compose up -d
```
L'application sera accessible sur `http://localhost:8000`.

Note: `verset.db` est monté dans le conteneur depuis le répertoire courant afin de persister les données.

## Build & run image Docker
```bash
docker build -t yourdockerhubuser/verset-app:latest .
docker run -e SECRET_KEY='votre_secret' -p 8000:8000 -v ${PWD}/verset.db:/app/verset.db yourdockerhubuser/verset-app:latest
```

## Déploiement automatique (GitHub Actions)
Le workflow `.github/workflows/docker-deploy.yml` construit et pousse l'image vers Docker Hub lors d'un push sur `main`.
Ajoutez ces Secrets dans GitHub: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.
Pour déployer automatiquement via SSH, ajoutez `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_KEY`.

## Déploiement manuel sur serveur distant
Copiez `verset.db` et le répertoire `static/` sur le serveur, placez `SECRET_KEY` dans les variables d'environnement, puis utilisez `deploy.sh` ou lancez manuellement `docker run`.

## Remarques de sécurité
- Ne commitez jamais `SECRET_KEY` ni `verset.db` dans le dépôt public.
- Pour une configuration scalable/HA, migrez vers PostgreSQL et utilisez `docker-compose` avec un service `db`.
