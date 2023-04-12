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

######################################
#TABLE ET CLASSE pour les informations sur les products 
class Product(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField()
    image = CharField()
    weight = IntegerField()
    price = FloatField()
    in_stock = BooleanField()

######################################
#TABLE ET CLASSE pour les informations sur le shipping information
class Shipping_Information(BaseModel):
    id = AutoField(primary_key=True)
    country = CharField()
    address = CharField()
    city = CharField()
    postal_code = CharField()
    province = CharField()

######################################
#TABLE ET CLASSE pour les informations de transaction
class Transaction(BaseModel):
    id = CharField(primary_key=True)
    success = BooleanField()
    amount_charged = IntegerField()

######################################
#TABLE ET CLASSE pour les informations sur la credit card 
class CreditCard(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    first_digits = CharField()
    last_digits = CharField()
    expiration_year = IntegerField()
    expiration_month = IntegerField()

######################################
#TABLE ET CLASSE pour les informations sur l'order réalisé
class Order(BaseModel):
    id = AutoField(primary_key=True)
    total_price = IntegerField()
    email = CharField(null=True)
    paid = BooleanField(default=False)
    shipping_price = FloatField()
    shipping_information = ForeignKeyField(Shipping_Information, backref="orders", null=True)
    transaction = ForeignKeyField(Transaction, backref="orders", null=True)
    credit_card = ForeignKeyField(CreditCard, backref="orders", null=True)

######################################
#TABLE ET CLASSE pour les informations des produits commandés et les quantités        
class CommandOrder(BaseModel):
    id = AutoField(primary_key=True)
    id_order = ForeignKeyField(Order, backref="command_order")
    id_product = ForeignKeyField(Product, backref="command_order")
    quantity = IntegerField()


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
    database.create_tables([Product, Shipping_Information, Transaction, CreditCard , Order, CommandOrder])
    click.echo("Initialized the database.")
        
def init_app(app):
    app.cli.add_command(init_db_command)
