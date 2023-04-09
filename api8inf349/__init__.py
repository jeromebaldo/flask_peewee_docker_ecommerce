from flask import Flask, jsonify, redirect, url_for, request, render_template
from peewee import *
from api8inf349.models.models import Product, init_app
from api8inf349.services.services_ext import API_Ext_Services
from api8inf349.services.services_int import API_Inter_Product_Services

from api8inf349.models.models import Product

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
        
        #1er ETAPE : verifier qu'il  y est au moins une commande 
        selected_products = []
        for key in request.form:
            if key.startswith('selected_product_'):
                product_id = request.form.get(key)
                quantity_key = f"product_quantity_{product_id}"
                quantity = request.form.get(quantity_key)
                selected_products.append({"id" : product_id, "quantity" : quantity})
        #return jsonify(products=selected_products), 200
        #2e ETAPE : verifier que les produits existent 
        for product in selected_products:
            if Product.get(Product.id == )
        #3e ETAPE : verifier que les produits soient en stocks 

        #4e ETAPE : verifier que les quantites pour chaque produit soit égal ou supérieur à 1 

    return app
