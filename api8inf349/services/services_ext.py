from flask import Flask, jsonify, redirect, url_for
from flask.cli import with_appcontext
from peewee import PostgresqlDatabase
#import click
import requests
import json

from api8inf349.models.models import Product

class API_Ext_Services(object):

    # methode pour récupérer tous les produits de l'API distante
    # suppression des éléments de la table Product et remplacement 
    @classmethod
    def update_products(cls):
        # Récupération des produits depuis l'API externe
        response = requests.get('http://dimprojetu.uqac.ca/~jgnault/shops/products/')
        data = response.json()

        # Suppression des produits existants dans la base de données
        Product.delete().execute()

        # Ajout des nouveaux produits à la base de données
        for product_data in data['products']:
            product_data = Product.create(
                id=product_data['id'],
                name=product_data['name'],
                description=product_data['description'],
                image=product_data['image'],
                weight=product_data['weight'],
                price=product_data['price'],
                in_stock=product_data['in_stock']      
            )

        