FROM python:3.9-slim-buster

# installation des dépendances
RUN apt-get update && apt-get install -y gcc libpq-dev python3-dev
COPY ./config_infos/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# copie des fichiers de l'application
COPY api8inf349 /api8inf349

# commande de lancement de l'application
CMD export FLASK_DEBUG=True && export FLASK_APP=api8inf349 && export DB_HOST=host.docker.internal && export DB_USER=user && export DB_PASSWORD=pass && export DB_PORT=5432 && export DB_NAME=api8inf349 && flask init-db && flask run --host=0.0.0.0

#REDIS_URL: redis://cache:6379/0