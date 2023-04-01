from flask import Flask
from peewee import *
import os

def create_app(initial_config=None):
    app = Flask("api8inf349")
    
    # récupération des informations de connexion à la base de données depuis les variables d'environnement
    db = PostgresqlDatabase(
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT']
    )

    # modèle de table
    class User(Model):
        username = CharField()
        email = CharField()

        class Meta:
            database = db
            table_name = 'users'

    # route de test
    @app.route('/')
    def index():
        with db.transaction():
            User.create(username= 'jerome', email='example@gmail.com')
        return 'Hello, World!'
    
    return app
