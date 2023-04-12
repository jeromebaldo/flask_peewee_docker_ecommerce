from flask import Flask, jsonify, redirect, url_for, request
from flask.cli import with_appcontext
from peewee import SqliteDatabase
import click
import requests
import json

from api8inf349.models.models import Product, Order, CommandOrder, Shipping_Information, CreditCard
from api8inf349.services.services_ext import API_Ext_Services
class API_Inter_Order_Services(object):
    
    #METHODE pour créer un ordre et l'ajouter dans la bd
    #calcul le total_price et le shipping price 
    @classmethod
    def crea_order(cls, selected_products):
        
        weight_total = 0
        total_price = 0
        shipping_price = 0
        for productSelec in selected_products:
            product = Product.get(id = productSelec['id'])
            weight_total += product.weight * int(productSelec['quantity'])
            total_price += product.price * int(productSelec['quantity'])
        
        if weight_total < 500:
            shipping_price = 5
        if weight_total >= 500 and weight_total < 2000:
            shipping_price = 10
        if weight_total >= 2000:
            shipping_price = 25

        order_cree = Order.create(total_price=total_price, shipping_price=shipping_price)
        
        for product in selected_products:
            CommandOrder.create(id_order=order_cree, id_product= product['id'], quantity=product['quantity'])

        return { 'id': order_cree.id}

    #METHODE pour verifier si l'order existe dans la base de données 
    #si non alors retourne code d'erreur 404 avec json adapté
    @classmethod
    def exist_order(cls,order_id):
        
        try:
            orderGet = Order.get(Order.id == order_id)
        except Order.DoesNotExist:
            error = {
                'order': {
                    'code': 'not-found',
                    'name': "La commande spécifiée n'existe pas"
                }
            }
            return {  'error' : error ,'code': 404}
        
        return {'code' : 200}

    #METHODE pour retourner l'order demandé avec tous les champs remplis ou non
    @classmethod
    def return_order(cls, order_id):
        
        #identification de l'order par son id 
        order = Order.get(id = order_id)

        #elaboration de la liste de l'order qui comprend toutes les informations 
        order_json= {
            'id': order.id,
            'total_price': order.total_price,
            'email': order.email,
            'paid': order.paid,
            'product': [],
            'shipping_price': order.shipping_price,
            "transaction": {},
            "credit_card": {},
            "shipping_information" : {}
        }
        
        #récupération des id product avec leur quantité
        #récupération par une requete select de l'ensemble des command_order lié à l'order 
        command_info = CommandOrder.select().where(CommandOrder.id_order == order.id)
        for command in command_info:
            order_json['product'].append({"id" : command.id_product.id, "quantity" : command.quantity})

        # Récupération des informations d'expédition
        if order.shipping_information is not None:
            shipping_info = order.shipping_information
            order_json['shipping_information'] = {
                'id': shipping_info.id,
                'country': shipping_info.country,
                'address': shipping_info.address,
            'city': shipping_info.city,
            'province': shipping_info.province
        }

        # Récupération des informations de transaction
        if order.transaction is not None:
            transaction = order.transaction
            order_json['transaction'] = {
                'id': transaction.id,
                'success': transaction.success,
                'amount_charged': transaction.amount_charged
            }

        # Récupération des informations de carte de crédit
        if order.credit_card is not None:
            credit_card = order.credit_card
            order_json['credit_card'] = {
                'id': credit_card.id,
                'name': credit_card.name,
                'first_digits': credit_card.first_digits,
                'last_digits': credit_card.last_digits,
                'expiration_year': credit_card.expiration_year,
                'expiration_month': credit_card.expiration_month
            }
        return order_json
    
    #METHODE pour  la mise à jour du shipping information 
    @classmethod
    def put_order_infoClient(cls,order_id, request):
        
        orderModif = None
        
        #verifier l'order existe
        response = API_Inter_Order_Services.exist_order(order_id)
        if int(response['code']) == 404:
            return {'error' : response['error'], 'code' : 404}
        else:
            orderModif = Order.get(Order.id == order_id) #recuperation de l'order
        
        #methode pour remplissage des champs ainsi que la conformité des champs
        response = API_Inter_Order_Services.verif_infoClient(request)
        if int(response['code']) != 200:
            return {'error': response['error'], 'code' : response['code']}

        #creation du shipping information et de la mise à jour de l'order    
        shipInfo = Shipping_Information.create(country=request.form['country'],address=request.form['address'],
                        city=request.form['city'],postal_code=request.form['postal_code'],province=request.form['province'])
        orderModif.email = request.form['email']
        orderModif.shipping_information = shipInfo
        orderModif.save()
        
        return {'order' : "shipping_information OK" ,'code': 200}
    
    #METHODE pour verifier tous les champs ainsi que leur remplissage
    @classmethod
    def verif_infoClient(cls,request):
        
        #verifier que tous les champs soient compris dedans 
        required_fields = {'email', 'country', 'address', 'postal_code', 'city', 'province'}
        
        # Vérifie si tous les champs requis sont présents dans la requête
        if not required_fields.issubset(request.form.keys()):
            
            error = {
                    'order': {
                        'code': 'missing-fields',
                        'name': "Il manque un ou plusieurs champs qui sont obligatoires"
                    }
                }
            return {'error' : error ,'code': 422}
        
        # Vérifier qu'il n'y a pas de champ supplémentaire dans la requête
        if not required_fields.union({'name'}).issuperset(request.form.keys()):
            
            error = {
                    'order': {
                        'code': 'invalid-fields',
                        'name': "Certains champs ne peuvent pas être modifiés par cette requête"
                    }
                }
            
            return {'error' : error ,'code': 422}

        # Vérifier que tous les champs sont remplis
        if not all(request.form.get(field) for field in required_fields):
            
            error = {
                    'order': {
                        'code': 'missing-fields',
                        'name': "Il faut les informations clients pour compléter la commande"
                    }
                } 
            
            return {'error': error, 'code': 422}
        
        return {'code': 200}
    
    #METHODE pour mettre à jour l'order et réaliser le paiement 
    @classmethod
    def put_order_paiement(cls,order_id, request):
        
        order_paiement = None

        #verifier l'order existe
        response = API_Inter_Order_Services.exist_order(order_id)

        if int(response['code']) == 404:
            return {'error' : response['error'], 'code' : 404}
        else:
            order_paiement = Order.get(Order.id == order_id) #recuperation de l'order
        
        #verifier et obliger le client à remplir l'email et le shippinginformation avant de payer 
        if order_paiement.email is None or order_paiement.shipping_information is None:
            return { 'error' : {'errors' : { "order": { "code": "missing-field", "name": "l'email et/ou les informations d'expéditions n'ont été rentrées " } } }, 'code': 422}
        
        # si paid  == true alors la commande est déjà payé et retourne 422 avec json d'informations 
        if order_paiement.paid == True:
            return { 'error' : {'errors' : { "order": { "code": "already-paid", "name": "La commande a déjà été payée." } } }, 'code': 422}
        
        #Vérification des champs donnés par la credit_card
        response = API_Inter_Order_Services.verif_creditCard(request)

        if int(response['code']) != 200:
            return {'error': response['error'], 'code' : response['code']}
        
        #recuperer le total price et le shipping price pour le total amount et creer le json pour paiement
        total_amount = order_paiement.total_price + order_paiement.shipping_price
        info_credit = { "credit_card" : {
                            "name" : request.form['name'], 
                            "number" : request.form['number'], 
                            "expiration_year" : request.form['expiration_year'], 
                            "cvv" : request.form['cvv'], 
                            "expiration_month" : request.form['expiration_month'] },
                        "amount_charged": total_amount
                    }
                
        # envoyer la demande de paiement 
        response = API_Ext_Services.to_verifCard(info_credit)
        if response['code'] != 200:
            return {'error': response['error'], 'code' : response['code']}
        
        #c'est la que je remplit le credit_card et transaction 
        # paid = true 
        CreditCard.create(name = response, first_digits = , last_digits = , expiration_year = , expiration_month = ,)


        """ "name" : John Doe
        "number" : 4242 4242 4242 4242 
        "expiration_year" : 2024 
        "cvv" : 123 
        "expiration_month" : 9 """
    
    @classmethod
    def verif_creditCard(cls,request):
        
        required_fields = {'name', 'number', 'expiration_month', 'expiration_year', 'cvv'}
        
        # Vérifie si tous les champs requis sont présents dans la requête
        if not required_fields.issubset(request.form.keys()):
            
            error = {
                    'order': {
                        'code': 'missing-fields',
                        'name': "Il manque un ou plusieurs champs qui sont obligatoires"
                    }
                }
            return {'error' : error ,'code': 422}
        
        # Vérifier qu'il n'y a pas de champ supplémentaire dans la requête
        if not required_fields.union({'name'}).issuperset(request.form.keys()):
            
            error = {
                    'order': {
                        'code': 'invalid-fields',
                        'name': "Certains champs ne peuvent pas être modifiés par cette requête"
                    }
                }
            
            return {'error' : error ,'code': 422}

        # Vérifier que tous les champs sont remplis
        if not all(request.form.get(field) for field in required_fields):
            
            error = {
                    'order': {
                        'code': 'missing-fields',
                        'name': "Il faut que les informations de la credit_card soient tous remplis"
                    }
                } 
            
            return {'error': error, 'code': 422}

        #verifier que les expiration year et month sont des integer car l'APi externe ne verifie pas ces champs
         #verifier que les expiration year et month sont des integer car l'APi externe ne verifie pas ces champs  
        """ if not isinstance(int(request.form['expiration_year']), int) or not isinstance(int(request.form['expiration_month']), int) :
            return {'error':  { 
                "order": { 
                    "code": "error-field", 
                    "name": "année d'expiration ou/et mois expiration invalide " 
                } }, 'code' : 422} """
        
        return {'code': 200}
        