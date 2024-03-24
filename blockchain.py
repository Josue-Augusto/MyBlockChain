import datetime
import hashlib
import json
from flask import Flask, jsonify

#Criar a blockchain
class Blockchain:
    def __init__(self): #Iniciando a classe
        self.chain = [] #Iniciando lista 
        self.create_block(data = 'Primeiro bloco',nonce = 1, previous_hash='0000000000000000000000000000000000000000000000000000000000000000' ) #Crinado o Genesis
        
    def create_block(self,data, nonce, previous_hash):
        nonce_operation = self.proof_of_work(data, previous_hash)
        hash_operation = self.hash(data, nonce_operation, previous_hash)
        block = {'index': len(self.chain)+ 1, #Tamanho da blockchain
             'timestamp': str(datetime.datetime.now()),
             'nonce': nonce, #Pegando o nounse minerado
             'previous_hash': previous_hash, #Hash anterior
             'data' : data,
             'hash_operation' : hash_operation
             } 
        self.chain.append(block)
        return block


    def get_previus_block(self): #Retornar o ultimo bloco
        return self.chain[-1]

    def proof_of_work(self, data, previous_hash): # Validando o nouse
        new_nonce = 1 #Nounse iniciado com 1
        check_nonce = False # controle de validação
        while check_nonce is False: #checando o os nounse
            hash_opreation = str(self.hash(data, new_nonce, previous_hash)) #Gerando Hash em String
            print(hash_opreation)
            if hash_opreation[:3] == '000': #Validadndo o Hash gerado 
               check_nonce = True
            else:
               new_nonce +=1
        return new_nonce
    
    def nounce_check(self, data, nonce, previous_hash): # Validando o nouse
        check_nonce = False # controle de validação
        hash_opreation = str(self.hash(data, nonce, previous_hash))#Gerando Hash em String
        if hash_opreation[:3] == '000': #Validadndo o Hash gerado 
           check_nonce = True
            
        return check_nonce

    def hash(self, data, new_nonce, previous_hash): #Criar Hash com Bloco em contrução
        block = {   
                    'nonce': new_nonce,
                    'previous_hash': previous_hash,
                    'data': data
                    }
        encode_hash = json.dumps(block, sort_keys=True).encode() #Transformando o bloco em Jason
        return hashlib.sha256(encode_hash).hexdigest() #Gerando Hash com bloco Jason

    def is_chain_valid(self, chain): #Percorrer a blockchain para validar todos os Hash's
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

app = Flask(__name__) #Inicializando Flask
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

Blockchain = Blockchain() #Instanciando a classe blockchain


@app.route('/mine_block', methods=['GET'])
def mine_block():
    data =' teste de bloco: '
    previus_block = Blockchain.get_previus_block() # Pegando o ultimo bloco
    previous_hash = previus_block['hash_operation']
    gold_nonce = Blockchain.proof_of_work(data, previous_hash) #validando o Nounse
    block = Blockchain.create_block(data,gold_nonce, previous_hash)
    response = {'message': 'Bloco minerado!',
                'index' : block['index'],
                'nonce' : block['nonce'],
                'previous_hash' : block['previous_hash'],
                'data' : block['data'],
                'hash_operation' : block['hash_operation']
                }
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])#retornando toda a blockchain
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



app.run(host='0.0.0.0', port=5000)

