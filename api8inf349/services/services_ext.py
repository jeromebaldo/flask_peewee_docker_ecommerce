from flask import Flask, jsonify, redirect, url_for
from flask.cli import with_appcontext
from peewee import PostgresqlDatabase
import requests
import json

from api8inf349.models.models import Product

class API_Ext_Services(object):

    # methode pour récupérer tous les produits de l'API distante
    # suppression des éléments de la table Product et remplacement 
    @classmethod
    def update_products(cls):

        #récupération des données sur l'API externe
        response = requests.get('http://dimprojetu.uqac.ca/~jgnault/shops/products/')
        data = response.json()

        # Suppression des produits existants dans la base de données
        Product.delete().execute()

        # Ajout des nouveaux produits à la base de données
        for product_data in data['products']:
            # supprimer les caractères nuls de la chaîne de caractères car blocage de mon client
            product_data = {key: value.replace('\x00', '') if isinstance(value, str) else value for key, value in product_data.items()}
            product = Product.create(**product_data)

        