from flask import Flask
from peewee import *
import os

from api8inf349.models.models import Product
from api8inf349.services.services_ext import API_Ext_Services

def create_app(initial_config=None):
    
    app = Flask("api8inf349")
    
    #mise à jour au démarrage de la table product avec API distante 
    def update_on_start():
        API_Ext_Services.update_products()
    update_on_start()

    
    @app.route('/')
    def index():
        #Product.create(name='Pommes', description='Un sac de pommes', image='pommes.jpg', weight=1, price=2.5, in_stock=True)
        return 'Hello, World!'
    
    return app
