FROM python:3.7-alpine
COPY api8inf349 /api8inf349
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 5000
CMD export FLASK_DEBUG=True && export FLASK_APP=api8inf349 && export DB_HOST=localhost && export DB_USER=user && export DB_PASSWORD=pass && export DB_PORT=5432 && export DB_NAME=api8inf349 && flask init-db && flask run --host=0.0.0.0
#CMD export FLASK_DEBUG=True && export FLASK_APP=api8inf349 && export DB_HOST=localhost && export DB_USER=user && export DB_PASSWORD=pass && export DB_PORT=5432 && export DB_NAME=api8inf349 && flask init-db && flask run
