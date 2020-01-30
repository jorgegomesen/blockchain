# Module 1 - Create a Blockchain

from datetime import datetime, timedelta
from copy import copy
import hashlib
import json
from flask import Flask, jsonify, request


# Part 1 - Building a Blockchain

class Document:
    def __init__(self, bidder, bidder_unit, crier):
        self.bidder = bidder,
        self.bidder_unit = bidder_unit,
        self.crier = crier,  # pregoeiro

    def __repr__(self):
        return "bidder: " + self.bidder[0] + ",\nbidder_unit: " + self.bidder_unit[0] + ",\ncrier: " + self.crier[0]

    def serialize(self):
        return {
            "bidder": self.bidder,
            "bidder_unit": self.bidder_unit,
            "crier": self.crier
        }


class Proposal:

    def __init__(self, name, value):
        self.company_name = name
        self.proposal_value = value

    def __repr__(self):
        return "company_name: " + self.company_name + ",\nvalue: " + str(self.proposal_value)

    def serialize(self):
        return {
            "company_name": self.company_name,
            "value": self.proposal_value
        }


class Bidding:
    trading_floor_count = 1

    def __init__(self, authority, deadline, bidder, bidder_unit, crier, bid_value, document_date,
                 documentation_address):
        self.trading_floor_number = str(self.__class__.trading_floor_count) + '/' + str(datetime.now().year),
        self.authority = authority,  # autoridade é quem assina o processo administrativo
        self.trading_floor_team = [],  # equipe de pregão escolhida pelo pregoeiro
        self.document = Document(bidder, bidder_unit, crier),  # edital
        self.created_at = datetime.now(),  # quando foi criada
        self.finish_at = datetime.now() + timedelta(days=int(deadline)),  # data limite para obter-se um proprietário
        self.owned_by = None,  # proprietário da licitação
        self.proposals = []  # propostas
        self.date_session = None,  # data da sessão
        self.time_session = None,  # horário da sessão
        self.bid_value = bid_value,  # valor da licitação
        self.document_date = document_date,  # data do edital
        self.documentation_address = documentation_address  # endereço para envio da documentação

        self.__class__.trading_floor_count += 1

    def __repr__(self):
        return "trading_floor_number: " + str(self.trading_floor_number) + ",\nauthority: " + self.authority[
            0] + ",\ntrading_floor_team: " + repr(self.trading_floor_team) + ",\ndocument: " + repr(
            self.document[0]) + ",\ncreated_at: " + str(self.created_at[0].timestamp()) + ",\nfinish_at: " + str(
            self.finish_at[
                0].timestamp()) + ",\nowned_by: " + str(self.owned_by[0]) + ",\nproposals: " + repr(self.proposals)

    def add_proposal(self, name, value):
        try:
            if datetime.now().timestamp() <= self.finish_at[0].timestamp():
                self.proposals.append(Proposal(name, value))
                return True
            return False
        except ValueError:
            return False

    def define_best_proposal(self):
        proposals = self.proposals
        min_value = proposals[0].proposal_value
        self.owned_by = proposals[0].company_name
        for proposal in proposals:
            if proposal.proposal_value < min_value:
                min_value = proposal.proposal_value
                self.owned_by = proposal.company_name

    def clone(self):
        authority = self.authority
        bidder = "deafult"
        bidder_unit = "deafult"
        crier = "deafult"
        deadline = 0  # em dias
        bid_value = self.bid_value
        document_date = self.document_date
        documentation_address = self.documentation_address
        new_bidding = Bidding(authority, deadline, bidder, bidder_unit, crier, bid_value, document_date,
                              documentation_address)
        new_bidding.finish_at = self.finish_at
        new_bidding.document = self.document
        new_bidding.proposals = copy(self.proposals)
        return new_bidding

    def serialize(self):
        proposals = self.proposals
        new_proposals = []

        for proposal in proposals:
            new_proposals.append(proposal.serialize())

        return {
            "trading_floor_number": self.trading_floor_number,
            "authority": self.authority,
            "trading_floor_team": self.trading_floor_team,
            "document": self.document[0].serialize(),
            "created_at": str(self.created_at[0].timestamp()),
            "finish_at": str(self.finish_at[0].timestamp()),
            "owened_by": self.owned_by,
            "proposals": new_proposals
        }


class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_block(proof=1, bid=None, previous_hash='0')

    def create_block(self, proof, bid, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'proof': proof,
            'bidding': bid,  # licitação
            'previous_hash': previous_hash
        }
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

    def is_chain_valid(self):
        previous_block = self.chain[0]
        block_index = 1
        chain_length = len(self.chain)
        while block_index < chain_length:
            block = self.chain[block_index]
            if block['previous_hash'] != self.hash(
                    self.serialize(previous_block) if previous_block['bidding'] else previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def serialize(self, block):
        return {
            "index": block['index'],
            "timestamp": block['timestamp'],
            "proof": block['proof'],
            "bidding": block['bidding'].serialize(),
            "previous_hash": block['previous_hash']
        }


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
