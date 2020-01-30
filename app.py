from flask import Flask, jsonify, request
from blockchain.Bidding import Bidding
from blockchain.Blockchain import Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# Creating a Bidding
openned_biddings = []

# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    if len(openned_biddings) < 1:
        return jsonify('Não existem licitações disponíveis para minerar-se.'), 500
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(
        blockchain.serialize(previous_block) if previous_block['bidding'] else previous_block)
    block = blockchain.create_block(proof, openned_biddings.pop(0), previous_hash)
    response = {'message': 'Bloco minerado com sucesso!',
                'bidding': blockchain.serialize(block)}
    return jsonify(response), 200


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain = []
    for block in blockchain.chain:
        if block['bidding']:
            chain.append(blockchain.serialize(block))
            continue
        chain.append(block)
    response = {
        'chain': chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


# Checking if block is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    valid = blockchain.is_chain_valid()
    response = {'message': ('Everything is ok.' if valid else 'Houston, we have a problem.')}
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
            deadline = request.form['deadline']  # em dias
            bid_value = request.form['bid_value']
            document_date = request.form['document_date']
            documentation_address = request.form['documentation_address']

            openned_biddings.append(
                Bidding(authority, deadline, bidder, bidder_unit, crier, bid_value, document_date,
                        documentation_address))

            return jsonify('Licitação criada com sucesso.'), 200
        except ValueError:
            return jsonify('Parâmetros inválidos.'), 400


# 2. Devolver solicitações
@app.route('/get_openned_biddings', methods=['GET'])
def get_openned_biddings():
    if request.method == 'GET':
        # biddings = bidding.get_openned_biddings()
        biddings_formated = []
        for bid in openned_biddings:
            biddings_formated.append(bid.serialize())
        return jsonify(biddings_formated), 200
    return 'Invalid request.', 400


# 3. Envio de proposta para solicitação m
@app.route('/send_proposal', methods=['POST'])
def send_proposal():
    if request.method == 'POST':
        try:
            index = int(request.form['bidding_id'])
            if index >= 0 & index < len(blockchain.chain):
                old_bidding = blockchain.chain[index]['bidding']
                new_bidding = old_bidding.clone()
                openned_biddings.append(new_bidding)
                new_bidding.add_proposal(request.form['name'], float(request.form['value']))
                return jsonify('OK'), 200
            return jsonify('ERROR'), 400
        except ValueError:
            return 'Invalid parameters', 200
    return 'Invalid request.', 400


# 4. Definir ganhador do proceso licitatório
@app.route('/define_owner', methods=['POST'])
def define_owner():
    if request.method == 'POST':
        try:
            index = int(request.form['bidding_id'])
            if index >= 0 & index < len(blockchain.chain):
                bidding = blockchain.chain[index]['bidding']
                new_bidding = bidding.clone()
                new_bidding.define_best_proposal()
                openned_biddings.append(new_bidding)
                return jsonify('OK'), 200
            return jsonify('ERROR'), 400
        except ValueError:
            return 'Invalid parameters', 200
    return 'Invalid request.', 400
# Running the app
# app.run(host='0.0.0.0', port=5000)
