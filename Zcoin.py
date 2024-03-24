import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:
    def __init__(self): 
        self.chain = [] 
        self.transactions = [] 
        self.create_block(data = 'Primeiro bloco',nonce = 1, previous_hash='0000000000000000000000000000000000000000000000000000000000000000' ) 
        self.nodes = set()
        
    def create_block(self,data, nonce, previous_hash):
        nonce_operation = self.proof_of_work(data, previous_hash)
        hash_operation = self.hash(data, nonce_operation, previous_hash)
        block = {'index': len(self.chain)+ 1, 
             'timestamp': str(datetime.datetime.now()),
             'nonce': nonce, 
             'previous_hash': previous_hash, 
             'data' : data,
             'hash_operation' : hash_operation,
             'transactions' : self.transactions 
             } 
        self.transactions = [] 
        self.chain.append(block)
        return block


    def get_previus_block(self): 
        return self.chain[-1]

    def proof_of_work(self, data, previous_hash): 
        new_nonce = 1 
        check_nonce = False 
        while check_nonce is False: 
            hash_opreation = str(self.hash(data, new_nonce, previous_hash)) 
            print(hash_opreation)
            if hash_opreation[:3] == '000': 
               check_nonce = True
            else:
               new_nonce +=1
        return new_nonce
    
    def nounce_check(self, data, nonce, previous_hash): 
        check_nonce = False 
        hash_opreation = str(self.hash(data, nonce, previous_hash))
        if hash_opreation[:3] == '000': 
           check_nonce = True
            
        return check_nonce

    def hash(self, data, new_nonce, previous_hash): 
        block = {   
                    'nonce': new_nonce,
                    'previous_hash': previous_hash,
                    'data': data
                    }
        encode_hash = json.dumps(block, sort_keys=True).encode() 
        return hashlib.sha256(encode_hash).hexdigest() 

    def is_chain_valid(self, chain): 
        previus_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash']!= previus_block['hash_operation']:
               return False
            hash_operation = str(self.hash(block['data'], block['nonce'], block['previous_hash']))
            if hash_operation[:3] != '000':
                return False
            previus_block = block 
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount' : amount
                                  })
        previus_block = self.get_previus_block()
        return previus_block['index'] + 1
    
    
    def add_node(self, address):
        parsed_url = urlparse(address) 
        self.nodes.add(parsed_url.netloc) 
    
    
    def replace_chain(self): 
        network = self.nodes 
        longest_chain = None 
        max_length = len(self.chain) 
        for node in network:
            response = request.get(f'http://{node}/get_chain') 
            print(response)
            if response.status_code == 200:
                length = response.json()['length'] 
                chain = response.json()['chain'] 
                if length > max_length and self.is_chain_valid(chain): 
                    max_length = length 
                    longest_chain = chain 
        if longest_chain: 
            self.chain = longest_chain 
            return True
        return False
   

app = Flask(__name__) 


node_address = str(uuid4()).replace('-', '')




app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

Blockchain = Blockchain() 


@app.route('/mine_block', methods=['GET'])
def mine_block():
    sender = node_address
    receiver = 'Josué'
    amount = 1
    Blockchain.add_transaction(sender, receiver, amount)
    data =' teste de bloco: '
    previus_block = Blockchain.get_previus_block() 
    previous_hash = previus_block['hash_operation']
    gold_nonce = Blockchain.proof_of_work(data, previous_hash) 
    
    block = Blockchain.create_block(data,gold_nonce, previous_hash)
    response = {'message': 'Bloco minerado!',
                'index' : block['index'],
                'nonce' : block['nonce'],
                'previous_hash' : block['previous_hash'],
                'data' : block['data'],
                'hash_operation' : block['hash_operation'],
                'transactions' : block['transactions']
                }
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': Blockchain.chain, 
                'length':len(Blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = Blockchain.is_chain_valid(Blockchain.chain)
    if is_valid:
        response = {'message' : 'Is Valid'}
    else:
        response = {'message' : 'Not Valid'}
    return jsonify(response), 200



@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json() 
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys): 
        return 'Invalid', 400 
    index = Blockchain.add_transaction(json['sender', 'receiver', 'amount'])
    response = {'message' : 'Sucesso ao add ao boloco: {index}'}
    return jsonify(response), 201 


@app.route('/connect_node', methods=['POST']) 
def connect_node():
    json = request.get_json() 
    nodes = json.get('nodes') 
    if nodes is None: 
        return 'invalid', 400 
    for node in nodes: 
        Blockchain.add_node(node) 
    response = {'message': 'Lista de Nós da rede',
                'Totla' : list(Blockchain.nodes)
                }
    return jsonify(response), 201
    

@app.route('/replace_chain', methods=['GET']) 
def replace_chain():
    is_chain_replaced = Blockchain.replace_chain() 
    if is_chain_replaced: 
        response = {'message' : 'redes conflitantes, ajuste ocorrido',
                    'blockchain': Blockchain.chain}
    else: 
        response = {'message' : 'Blockchain valido',
                    'blockchain': Blockchain.chain}
    return jsonify(response), 201



app.run(host='0.0.0.0', port=5000)

