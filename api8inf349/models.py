import os
import click
from flask.cli import with_appcontext
from peewee import Model, PostgresqlDatabase, AutoField, CharField, IntegerField, BooleanField, FloatField
from playhouse.postgres_ext import *


def get_db():
    return {
        'user': os.environ.get('DB_USER', 'user'),
        'password': os.environ.get('DB_PASSWORD', 'pass'),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', '5432'))
    }

class BaseModel(Model):
    class Meta:
        database = PostgresqlDatabase('api8inf349',**get_db())


class Product(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField()
    image = CharField()
    weight = IntegerField()
    price = FloatField()
    in_stock = BooleanField()


@click.command("init-db")
@with_appcontext
def init_db_command():
    database = PostgresqlDatabase('api8inf349',**get_db())
    database.create_tables([Product])
    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(init_db_command)
