from datetime import datetime
import hashlib
import json


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
