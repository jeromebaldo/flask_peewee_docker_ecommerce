from flask import Flask, jsonify, redirect, url_for, request, render_template
from peewee import *
from redis import Redis
import os
import json
from api8inf349.models.models import Product, Order, CommandOrder, init_app

from rq import Queue, Worker

from api8inf349.services.services_ext import API_Ext_Services
from api8inf349.services.services_int_product import API_Inter_Product_Services
from api8inf349.services.services_int_order import API_Inter_Order_Services

redis = Redis(host=os.environ['REDIS_HOST'], port=6379, db=0)
queue = Queue(connection=redis)

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
            return jsonify(response['errors']), 422
        
        ### 3e ETAPE : verifier que les produits existent 
        
        response = API_Inter_Product_Services.exist_products(selected_products)
        #si le code est égale à 422 alors erreur
        if response['code'] == 422:
            return jsonify(response['errors']), 422
             
        ### 4e ETAPE : verifier que les produits soient en stocks
        
        response = API_Inter_Product_Services.stock_products(selected_products)
        #si le code est égale à 422 alors erreur
        if response['code'] == 422:
            return jsonify(response['errors']), 422
        
        ### 5e ETAPE : verifier que les quantites pour chaque produit soit égal ou supérieur à 1
        
        response = API_Inter_Product_Services.qtite_products(selected_products)
        #si le code est égale à 422 alors erreur
        if response['code'] == 422:
            return jsonify(response['errors']), 422

        ### 6e ETAPE : créer l'order avec les products et les quantités (table order + commandOrder)

        response = API_Inter_Order_Services.crea_order(selected_products)

        ### 7e ETAPE: retourner le lien de l'order crée

        lien_order = url_for('get_order', order_id = response['id'] , _external=True)
        return jsonify({'lien_order': lien_order}), 302

    ############################################
    #ROUTE qui affiche l'order ciblé par son ID 
    @app.route('/order/<int:order_id>', methods=['GET'])
    def get_order(order_id):
        
        response = []
        base = None
        ### 1er ETAPE : Recuperation de l'order dans redis si déja payé sinon consultation postgresSQL
        
        order_redis = redis.get(order_id)
        if order_redis:
            response = json.loads(order_redis)
            base = "REDIS"
            return render_template('info_commande.html', order=response, order_id=order_id, base=base), 200

        ### 2e ETAPE : vérifier que l'order est bien enregistré dans postgresSQL
        
        response = API_Inter_Order_Services.exist_order(order_id)
        if response['code'] == 404:
            return jsonify(response['error']), 404
        
        ### 3e ETAPE : retourner le json de l'order cible 
        
        response = API_Inter_Order_Services.return_order(order_id)
        base = "POSTGRES"
        return render_template('info_commande.html', order=response, order_id=response['id'], base=base), 200

    ############################################
    #ROUTE qui met à jour le shipping information ou réalise le paiement de l'order 
    @app.route('/order/<int:order_id>', methods=['POST'])
    def verif_put(order_id):
        
        #si le champ envoyé par le formulaire comprend email alors shipping information 
        if 'email' in request.form:
             
            response = API_Inter_Order_Services.put_order_infoClient(order_id, request)

            if response['code'] == 200:
                #si succes alors retourne le lien du get pourvoir l'état de la commande 
                lien_order = url_for('get_order', order_id = order_id , _external=True)
                return jsonify({'lien_order': lien_order})
        
            else:
               return jsonify(response['error']), response['code'] 
            
        #si le champ envoyé par le formulaire comprend name alors credit-card 
        elif 'name' in request.form:
            
            response = API_Inter_Order_Services.put_order_paiement(order_id, request)
            if response['code'] == 200:
                
                #l'order a été payé ainsi je l'inclue dans le redis avec l'id de l'order comme clé 
                order = Order.get(id= order_id)
                shipping_info = order.shipping_information
                transac_info = order.transaction
                credit_info = order.credit_card
                order_final = { "order" : 
                                { 
                                    'id' : order_id,
                                    'email' : order.email,
                                    'total_price' : order.total_price,
                                    'shipping_price': order.shipping_price,
                                    'paid': order.paid,
                                    'products' : [],
                                    'shipping_information' : {
                                        'country': shipping_info.country,
                                        'address': shipping_info.address,
                                        'city': shipping_info.city,
                                        'province': shipping_info.province},
                                    'credit_card' : { 
                                        'name': credit_info.name,
                                        'first_digits': credit_info.first_digits,
                                        'last_digits': credit_info.last_digits,
                                        'expiration_year': credit_info.expiration_year,
                                        'expiration_month': credit_info.expiration_month},
                                    'transaction': { 
                                        'id': transac_info.id_transac,
                                        'success': transac_info.success,
                                        'amount_charged': transac_info.amount_charged,
                                        'error' : {} }
                                }}

                command_info = CommandOrder.select().where(CommandOrder.id_order == order.id)
                for command in command_info:
                    order_final['order']['products'].append({"id" : command.id_product.id, "quantity" : command.quantity})
                
                order_redis = json.dumps(order_final)
                redis.set(order_id, order_redis)
                
                #succes du paiement alors on revient sur get order pour voir l'état de la commande
                lien_order = url_for('get_order', order_id = order_id , _external=True)
                return jsonify({'lien_order': lien_order})

            else:
               return jsonify(response['error']), response['code']
        
        else:
            
            error = { "error" : {
            'code': 'No email or name in form data'
            }}
            return jsonify(error), 422
        
    return app
