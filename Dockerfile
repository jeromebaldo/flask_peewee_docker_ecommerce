FROM python:3.9-slim-buster

# installation des dépendances
RUN apt-get update && apt-get install -y gcc libpq-dev python3-dev
COPY ./config_infos/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# copie des fichiers de l'application
COPY api8inf349 /api8inf349


