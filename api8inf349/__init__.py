from flask import Flask, jsonify, redirect, url_for, request, render_template
from peewee import *
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

        products = []
        products = API_Inter_Product_Services.list_Total_Product()

        return render_template('product.html', products=products), 200
    
    @app.route('/order', methods=['POST'])
    def create_order():#creation d'un order 
        
        #1er ETAPE verifier le produit existe 
        response = API_Inter_Product_Services.exist_product(request)
        if response['code'] != 200:
            return jsonify(response['errors']), response['code']


    return app
