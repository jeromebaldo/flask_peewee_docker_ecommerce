from flask import Flask, jsonify, redirect, url_for, request
from flask.cli import with_appcontext
from api8inf349.models import Product
import click
import requests
import json



#################################################################################
###########METHODES D'APPEL POUR LES API EXTERNES DE L'APPLICATION###############
class API_Ext_Services(object):

    #########METHODE POUR RECUPERER TOUS LES PRODUCTS SUR SERVEUR EXTERNE########## 
    ## L'OBJECTIF EST DE METTRE A JOUR LA TABLE PRODUCT   
    @classmethod
    def update_products(cls):
        # Récupération des produits depuis l'API externe
        response = requests.get('http://dimprojetu.uqac.ca/~jgnault/shops/products/')
        data = response.json()

        # Suppression des produits existants dans la base de données
        Product.delete().execute()

        # Ajout des nouveaux produits à la base de données
        for product_data in data['products']:
            product = Product.create(
                id=product_data['id'],
                name=product_data['name'],
                description=product_data['description'],
                image=product_data['image'],
                weight=product_data['weight'],
                price=product_data['price'],
                in_stock=product_data['in_stock']      
            )


#################################################################################
###########METHODES D'APPEL POUR LES API INTERNES DE L'APPLICATION###############
class API_Inter_Product_Services(object):
    
    #########METHODE POUR RECUPERER TOUS LES PRODUCTS DANS BD########## 
    @classmethod
    def list_Total_Product(cls):
        
        products = Product.select()
        product_list = []
        
        for product in products:
            product_ligne = {'id': product.id,
                'name': product.name,
                'description': product.description,
                'image' : product.image,
                'weight' : product.weight,
                'price': product.price,
                'in_stock': product.in_stock}
            product_list.append(product_ligne)
        
        return product_list