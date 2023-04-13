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

        # Récupération des données sur l'API externe
        response = requests.get('http://dimprojetu.uqac.ca/~jgnault/shops/products/')
        data = response.json()

        # Parcours de tous les produits de l'API externe
        for product_data in data['products']:

            # Supprimer les caractères nuls de la chaîne de caractères car blocage de mon client
            product_data = {key: value.replace('\x00', '') if isinstance(value, str) else value for key, value in product_data.items()}
            
            # Récupération du produit correspondant dans la base de données
            existing_product = Product.get_or_none(Product.id == product_data['id'])
            if existing_product is None:
                # Le produit n'existe pas encore dans la base de données, on le crée
                product = Product.create(**product_data)
            
            else:
            # Le produit existe déjà dans la base de données, on le met à jour
                existing_product.name = product_data['name']
                existing_product.description = product_data['description']
                existing_product.image = product_data['image']
                existing_product.weight = product_data['weight']
                existing_product.price = product_data['price']
                existing_product.in_stock = product_data['in_stock']
                existing_product.save()
    
    @classmethod
    def to_verifCard(cls,data):
        
        #prise de l'URL est requete dessus pour une réponse 
        url = 'http://dimprojetu.uqac.ca/~jgnault/shops/pay/'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        
        #selon le cas, retourne erreur ou les infos de transactions 
        if response.status_code == 200:
            transaction_data = response.json()
            return {'transaction' : transaction_data, 'code' : 200}
        else:
            error_data = response.json().get('errors')
            return {'error': error_data, 'code' : response.status_code}
        