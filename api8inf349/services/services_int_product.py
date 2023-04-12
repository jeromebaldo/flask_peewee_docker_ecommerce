#from flask import Flask, jsonify, redirect, url_for
#from flask.cli import with_appcontext
#from peewee import PostgresqlDatabase


from api8inf349.models.models import Product

class API_Inter_Product_Services(object):

    #METHODE qui recupère tous les produits présents dans la base de données pour leur affichage
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
    
    #METHODE qui met en forme la reponse HTTP et retourner le json de products (id + quantity)
    @classmethod
    def mise_forme(cls, request):
        
        selected_products = []

        for key in request.form:
            if key.startswith('selected_product_'):
                product_id = request.form.get(key)
                quantity_key = f"product_quantity_{product_id}"
                quantity = request.form.get(quantity_key)
                selected_products.append({"id" : product_id, "quantity" : quantity}) 

        return selected_products
    
    #METHODE qui verifie si le client a bien sélectionné au moins un produit 
    # s'il n'existe pas alors retourne un code 422 avec json 
    @classmethod
    def select_products(cls,selected_products):
        
        if len(selected_products) == 0:
            return {
                'errors': {
                    'product': {
                        'code': 'missing-fields',
                        'name': "La creation d'une commande necessite un produit"
                    }
                }
            ,'code': 422}
        
        return {'code': 200}
    
    #METHODE pour vérifier si les produits sélectionnés existent dans la base de données 
    @classmethod
    def exist_products(cls,selected_products):
        
        for product in selected_products:
            
            product_id = product['id']
            
            try:
                product_in_db = Product.get(Product.id == product['id'])
            except Product.DoesNotExist:
                return {
                'errors': {
                    'product': {
                        'code': 'invalid-product',
                        'name': "un ou plusieurs produits n'existent pas dans la base"
                    }
                }
            , 'code': 422}
            
            return {'code': 200}
    
    #METHODE qui vérifie si les produits sont en stock (in_stock = true)
    @classmethod
    def stock_products(cls,selected_products):
        
        for product in selected_products:
            
            product_id = product['id']
            
            try:
                product_in_db = Product.get(Product.id == product_id, Product.in_stock == True)
            except Product.DoesNotExist:
               return {
                'errors': {
                    'product': {
                        'code': 'out-of-inventory',
                        'name': "Le produit ou les produits ne sont demandes ne sont pas en inventaire"
                    }
                }
            , 'code': 422} 
        
        return {'code': 200}
    
    #METHODE qui vérifie si les quantités pour chaque produit sélectionné est égale ou supérieur à 1
    @classmethod
    def qtite_products(cls,selected_products):
        
        for product in selected_products:
            
            if int(product['quantity']) < 1:
                return {
                'errors': {
                    'product': {
                        'code': 'missing-fields',
                        'name': "La quantité doit être supérieure ou égale à 1"
                    }
                }
            , 'code': 422}
        
        return {'code': 200}
