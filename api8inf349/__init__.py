from flask import Flask, jsonify, redirect, url_for, request
from peewee import *
import os
import requests
from api8inf349.models.models import Product, init_app
from api8inf349.services.services_ext import API_Ext_Services
from api8inf349.services.services_int import API_Inter_Product_Services

def create_app(initial_config=None):
    app = Flask("api8inf349")
    init_app(app)

    @app.before_first_request
    def update_on_start():
        if Product.table_exists(): # pour eviter la collision entre init-db et la mise à jour 
            API_Ext_Services.update_products()       
    update_on_start()    

    
    @app.route('/', methods=['GET'])
    def get_products():
        product_list = []
        product_list = API_Inter_Product_Services.list_Total_Product()
        return jsonify({"products": product_list}), 200
    
    return app
