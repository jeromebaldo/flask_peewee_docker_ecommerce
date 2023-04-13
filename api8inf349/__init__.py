from flask import Flask, jsonify, redirect, url_for, request, render_template
from peewee import *
from redis import Redis
import os

from api8inf349.models.models import Product, init_app

from api8inf349.services.services_ext import API_Ext_Services
from api8inf349.services.services_int_product import API_Inter_Product_Services
from api8inf349.services.services_int_order import API_Inter_Order_Services



redis = Redis(host="cache", port=6379, db=0)

#os.environ['DB_NAME']
def create_app(initial_config=None):
    
    app = Flask("api8inf349")
    init_app(app)

    @app.before_first_request
    def update_on_start():
        if Product.table_exists(): # pour eviter la collision entre init-db et la mise à jour 
            API_Ext_Services.update_products()       
    update_on_start()    

    ############################################
    #ROUTE qui affiche tous les produits dans le tableau 
    @app.route('/', methods=['GET'])
    def get_products():

        products = []
        products = API_Inter_Product_Services.list_Total_Product()

        return render_template('product.html', products=products), 200
    
    ############################################
    #ROUTE qui crée un order en prenant en compte 
    #les products sélectionnés avec leurs quantités 
    @app.route('/order', methods=['POST'])
    def create_order():#creation d'un order 
        
        response = []
        selected_products = []

        ### 1er ETAPE : recuperation de la requête et mise en forme de la reponse du formulaire 
        
        selected_products = API_Inter_Product_Services.mise_forme(request)
                
        ### 2e ETAPE : verifier qu'il y est au moins une commande 
        
        response = API_Inter_Product_Services.select_products(selected_products)
        #si le code est égale à 422 alors erreur
        if response['code'] == 422:
            return jsonify(response['errors']), response['code']
        
        ### 3e ETAPE : verifier que les produits existent 
        
        response = API_Inter_Product_Services.exist_products(selected_products)
        #si le code est égale à 422 alors erreur
        if response['code'] == 422:
            return jsonify(response['errors']), response['code']
             
        ### 4e ETAPE : verifier que les produits soient en stocks
        
        response = API_Inter_Product_Services.stock_products(selected_products)
        #si le code est égale à 422 alors erreur
        if response['code'] == 422:
            return jsonify(response['errors']), response['code']
        
        ### 5e ETAPE : verifier que les quantites pour chaque produit soit égal ou supérieur à 1
        
        response = API_Inter_Product_Services.qtite_products(selected_products)
        #si le code est égale à 422 alors erreur
        if response['code'] == 422:
            return jsonify(response['errors']), response['code']

        ### 6e ETAPE : créer l'order avec les products et les quantités (table order + commandOrder)

        response = API_Inter_Order_Services.crea_order(selected_products)

        ### 7e ETAPE: retourner le lien de l'order crée

        lien_order = url_for('get_order', order_id = response['id'] , _external=True)
        return jsonify({'lien_order': lien_order})

    ############################################
    #ROUTE qui affiche l'order ciblé par son ID 
    @app.route('/order/<int:order_id>', methods=['GET'])
    def get_order(order_id):
        
        response = []

        ### 1er ETAPE : vérifier que l'order est bien enregistré dans la base 
        
        response = API_Inter_Order_Services.exist_order(order_id)
        if response['code'] == 404:
            return jsonify(response['error']), response['code']
        
        ### 2e ETAPE : retourner le json de l'order cible 
        
        response = API_Inter_Order_Services.return_order(order_id)
        
        return render_template('info_commande.html', order=response, order_id=response['id']), 200

    ############################################
    #ROUTE qui met à jour le shipping information ou réalise le paiement de l'order 
    @app.route('/order/<int:order_id>', methods=['POST'])
    def verif_put(order_id):
        
        #si le champ envoyé par le formulaire comprend email alors shipping information 
        if 'email' in request.form:
             
            response = API_Inter_Order_Services.put_order_infoClient(order_id, request)

            if response['code'] == 200:
                return jsonify(response['order']), response['code']
            else:
               return jsonify(response['error']), response['code'] 
            
        #si le champ envoyé par le formulaire comprend name alors credit-card 
        elif 'name' in request.form:
            
            response = API_Inter_Order_Services.put_order_paiement(order_id, request)
            if response['code'] == 200:
                ##############################
                ##############################
                #########c'est là que je récupère le json pour le mettre dans le redis 
                return jsonify(response['order']), response['code']
            else:
               return jsonify(response['error']), response['code']
        
        else:
            
            error = { "error" : {
            'message': 'No email or name in form data'
            }}
            return jsonify(error), 400
        
    return app
