from peewee import *
import os
from peewee import Model, PostgresqlDatabase, AutoField, CharField, IntegerField, FloatField, BooleanField
import click
from flask.cli import with_appcontext

# Configuration de la base de données
db = PostgresqlDatabase(
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT']
)

# Définition du modèle Product
class Product(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField()
    image = CharField()
    weight = IntegerField()
    price = FloatField()
    in_stock = BooleanField()

    class Meta:
        database = db
        table_name = 'product'

# Fonction pour initialiser la base de données avec les données initiales

@click.command("init-db")
@with_appcontext  
def init_db_command():
    if not Product.table_exists():
        db.create_tables([Product])
        click.echo("Initialized the database.")
        
def init_app(app):
    app.cli.add_command(init_db_command)