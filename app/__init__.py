from flask import Flask, request, jsonify
import pymongo
from dotenv import load_dotenv
from os import getenv

load_dotenv()

app = Flask(__name__)
# Faça a conexã com o MongoDB.
client = pymongo.MongoClient()

# Métodos auxiliares
def JsonEncoder(cursor):
    data = []
    for doc in cursor:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
            data.append(doc)
    return jsonify(data)

class Product:
    # Crie um atributo de classe que pegue a variável de ambiente DATABASE e crie/acesse o banco de dados.
    # Utilize essa variável em seus métodos.
    db = client[getenv('DATABASE')]
    
    def __init__(self, name, price, in_stock) -> None:
        self.name = name
        self.price = price
        self.in_stock = in_stock

    def register_product(self):
        # Desenvolva aqui a lógica para inserir um dado no banco.
        self.db.stock.insert_one({'name': self.name, 'price': self.price,'in_stock': self.in_stock})

    @classmethod
    def all_products(cls):
        # Desenvolva aqui a lógica para capturar todos os dados do banco.
        # Observem o erro você pode ter a necessidade de deletar um dado onde retorne um valor inválido para o flask.
        cursor = cls.db.stock.find()
        return JsonEncoder(cursor)

    @classmethod
    def product_by_name(cls, name):
        # Desenvolva aqui a lógica para capturar um dado específico pelo "name".
        cursor = cls.db.stock.find({'name': name})
        if isinstance(cursor,dict):
            return jsonify(cursor)
        else:
            return JsonEncoder(cursor)

    @classmethod
    def updated_product(cls, name, data_updated):
        # Desenvolva aqui a lógica para fazer a atualização dos dados, identificando qual dado deve ser utilizado e assim atualiza-lo.
        cursor = cls.db.stock.find({'name': name})
        update = {"$set": {}}
        for key in data_updated:
            update['$set'][key] = data_updated[key]
        if isinstance(cursor,dict):
            cls.db.stock.find_one_and_update({'name': name}, update, upsert=False)
            cursor = cls.db.stock.find({'name': name})
            return jsonify(cursor)
        else:
            cls.db.stock.update_many({'name': name}, update, upsert=False)
            cursor = cls.db.stock.find({'name': name})
            return JsonEncoder(cursor)
            

    @classmethod
    def delete_product(cls, name):
        # Por fim desenvolva aqui a lógica para fazer a deleção do dado a partir do "name".
        cls.db.stock.delete_many({'name':name})        

# Rotas

@app.post('/products')
def register():
    req = request.get_json()
    print(req)
    newProduct = Product(req['name'],req['price'],req['in_stock'])
    newProduct.register_product()
    # Utilize sua classe Product para criar e registrar o produto.

    return {'msg': 'created'}, 201

@app.get('/products')
def get_all():
    return Product.all_products()

@app.get('/products/<product_name>')
def get_by_name(product_name):
    # Utilize sua classe para retornar um dado específico do seu banco de dados pelo "name".

    return Product.product_by_name(str(product_name))

@app.patch('/products/<product_name>')
def update(product_name):
    req = request.get_json()
    
    return Product.updated_product(product_name,req)
    # Utilize o método da sua classe para fazer a operação de atualizar os dados, passando seus respectivos parâmetros.

@app.delete('/products/<product_name>')
def delete(product_name):
    # Utilize o método da sua classe para fazer a operação de deletar os dados, passando seu respectivo parâmetro.
    Product.delete_product(product_name)
    return {
        "msg": "product deleted"
    }, 200