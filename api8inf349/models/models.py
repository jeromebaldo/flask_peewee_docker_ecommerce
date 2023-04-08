from peewee import *
import os
from peewee import Model, PostgresqlDatabase, AutoField, CharField, IntegerField, FloatField, BooleanField
import click
from flask.cli import with_appcontext
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = PostgresqlDatabase(
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        )

class Product(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField()
    image = CharField()
    weight = IntegerField()
    price = FloatField()
    in_stock = BooleanField()

class Poll(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(null=False)
    date = DateTimeField()

class Choice(BaseModel):
    id = AutoField(primary_key=True)
    choice = CharField(null=False)
    poll = ForeignKeyField(Poll, backref="choices")

class VoteCast(BaseModel):
    id = AutoField(primary_key=True)
    poll = ForeignKeyField(Poll, backref="vote_casts")
    choice = ForeignKeyField(Choice, backref="vote_casts")

   
# Fonction pour initialiser la base de données avec les données initiales
@click.command("init-db")
@with_appcontext  
def init_db_command():
    database = PostgresqlDatabase(
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT']
    )
    database.create_tables([Product, Poll, Choice, VoteCast])
    click.echo("Initialized the database.")
        
def init_app(app):
    app.cli.add_command(init_db_command)
