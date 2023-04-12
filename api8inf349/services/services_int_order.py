from flask import Flask, jsonify, redirect, url_for, request
from flask.cli import with_appcontext
from peewee import SqliteDatabase
import click
import requests
import json

from api8inf349.models.models import Product, Order, CommandOrder

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