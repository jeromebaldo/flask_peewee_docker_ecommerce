from flask import Flask, jsonify, redirect, url_for
from flask.cli import with_appcontext
from peewee import PostgresqlDatabase
import requests
import json

from api8inf349.models.models import Product

class API_Inter_Product_Services(object):

    #recupère tous les produits présents dans la base de données 
    @classmethod
    def list_Total_Product(cls):
        
        #récupération de toute la liste de produit 
        products = Product.select()
        #initialisation de list pouvant accueillir tous ces produits 
        product_list = []

        #boucle pour incrémenter chaque ligne
        for product in products:
            product_ligne = {'id': product.id,
                'name': product.name,
                'description': product.description,
                'image' : product.image,
                'weight' : product.weight,
                'price': product.price,
                'in_stock': product.in_stock}
            product_list.append(product_ligne)#append permet d'incrementer la ligne 
        
        return product_list