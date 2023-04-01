from flask import Flask, jsonify, redirect, url_for, request
from flask.cli import with_appcontext
from api8inf349 import view
from api8inf349.models import init_app
from api8inf349.services import API_Inter_Product_Services


def create_app(initial_config=None):
    
    app = Flask("api8inf349")
    init_app(app)

    @app.route('/', methods=['GET'])
    def get_products():
        #reprendre le chargement des produits
        product_list = []
        product_list = API_Inter_Product_Services.list_Total_Product() 
        return view.get_listProduit()

    return app