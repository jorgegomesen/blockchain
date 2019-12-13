# Module 1 - Create a Blockchain

from datetime import datetime, timedelta
from copy import copy
import hashlib
import json
from flask import Flask, jsonify, request


# Part 1 - Building a Blockchain

class Document:
    def __init__(self, bidder, bidder_unit, crier):
        self.bidder = bidder
        self.bidder_unit = bidder_unit
        self.crier = crier,  # pregoeiro
        # self.tradding_floot_num = tradding_floor_num
        pass


class Proposal:

    def __init__(self, name, value):
        self.company_name = name
        self.proposal_value = value

    # def create_proposal(self, name, value):
    #     proposal = {
    #         'name': name,
    #         'value': value
    #     }
    #     self.proposals.append(proposal)
    #     return proposal


class Bidding:

    def __init__(self, authority, document, deadline):
        self.authority = authority,  # autoridade é quem assina o processo administrativo
        self.trading_floor_team = [],  # equipe de pregão escolhida pelo pregoeiro
        self.document = document,  # edital
        self.created_at = datetime.now(),  # quando foi criada
        self.finish_at = datetime.now() + timedelta(days=deadline),  # data limite para obter-se um proprietário
        self.owned_by = None,  # proprietário da licitação
        self.proposals = []  # propostas

    def add_proposal(self, name, value):
        try:
            if datetime.now() <= self.finish_at:
                self.proposals.append(Proposal(name, value))
                return True
            return False
        except ValueError:
            return False

    def define_best_proposal(self):
        proposals = self.proposals
        min_value = proposals[0].value
        self.owned_by = proposals[0].name
        for proposal in proposals:
            if proposal.value < min_value:
                min_value = proposal.value
                self.owned_by = proposal.name


class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_block(proof=1, bid=None, previous_hash='0')

    def create_block(self, proof, bid, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.now()),
                 'proof': proof,
                 'bidding': bid,  # licitação
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                new_proof += 1
                continue
            check_proof = True
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        chain_length = len(chain)
        while block_index < chain_length:
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True


# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# Creating a Bidding
openned_biddings = []


# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'block': block}
    return jsonify(response), 200


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Checking if block is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    response = {'message': ('Everything is ok.' if is_valid else 'Houston, we have a problem.')}
    return jsonify(response), 200


# Bidding Routes

# 1. Solicitação de licitação
@app.route('/create_bidding', methods=['POST'])
def create_bidding():
    if request.method == 'POST':
        try:
            # (self, authority, document, applicant_institution, limit_date):
            authority = request.form['authority']
            bidder = request.form['bidder']
            bidder_unit = request.form['bidder_unit']
            crier = request.form['crier']
            deadline = request.form['deadline'] # em dias

            openned_biddings.append(Bidding(authority, Document(bidder, bidder_unit, crier), deadline))

            # a = copy(bidding.create_bidding(description))
            # a['created_at'] = str(a['created_at']);
            # a['finish_at'] = str(a['finish_at']);
            # proposals = a['proposals'].proposals
            # del a['proposals']
            # return jsonify({'bidding': a, 'proposals': proposals}), 200
        except ValueError:
            return 'Invalid parameters', 200


# # 2. Devolver solicitações
# @app.route('/get_openned_biddings', methods=['GET'])
# def get_openned_biddings():
#     if request.method == 'GET':
#         biddings = bidding.get_openned_biddings()
#         biddings_formated = []
#         for bid in biddings:
#             aux = copy(bid)
#             proposals = aux['proposals'].proposals
#             del aux['proposals']
#             biddings_formated.append({'bidding': aux, 'proposals': proposals})
#         return jsonify(biddings_formated), 200
#     return 'Invalid request.', 400
#
#
# # 3. Envio de proposta para solicitação m
# @app.route('/send_proposal', methods=['POST'])
# def send_proposal():
#     if request.method == 'POST':
#         try:
#             response = bidding.add_proposal(request.form['bidding_id'], request.form['name'], request.form['value'])
#             if response:
#                 return jsonify('OK'), 200
#             return jsonify('ERROR'), 400
#         except ValueError:
#             return 'Invalid parameters', 200
#     return 'Invalid request.', 400


# 4. Fechar licitação ( após prazo )
# 5. Devolver a licitação corrente

# Running the app
app.run(host='0.0.0.0', port=5000)
