
from hashlib import sha256
import json
from time import time
from flask import Flask, jsonify, request

class Blockchain(object):

	
	def __init__(self):
		self.chain = []
		self.current_transactions = []
		self.new_block(proof=42, previous_hash=42)

	def new_block(self, proof, previous_hash):
		block = {
		'index': len(self.chain) + 1,
		'timestamp': time(),
		'transactions': self.current_transactions,
		'proof': proof,
		'previous_hash': previous_hash,
		}
		self.current_transactions = []
		self.chain.append(block)
		return block
 
	def new_transaction(self, sender, recipient, amount):
		self.current_transactions.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
		})
		return self.last_block['index'] + 1

	def compute_hash(self, block):
		blockstr = json.dumps(block, sort_keys=True).encode()
		return sha256(blockstr).hexdigest()
	
	def proof_of_work(self, last_proof):
		new_proof = 1
		check_proof = False
		while check_proof is False:
			hash_operation = sha256((str(last_proof) + str(new_proof)).encode()).hexdigest()
			if hash_operation[-4:] == '4242':
				check_proof = True
			else:
				new_proof += 1
			print(hash_operation)
		return new_proof

	@property
	def last_block(self):
		return self.chain[-1]

blockchain = Blockchain()
app = Flask("pakisnet")

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	values = request.get_json()

	required = ['sender', 'recipient', 'amount']
	if not all(k in values for k in required):
		return 'Missing values', 400
	
	index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
	response = {'message': 'Transaction will be added to Block {0}'.format(index)}
	return jsonify(response), 201

@app.route('/mine', methods=['GET'])
def mine_block():
	
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)

	blockchain.new_transaction(
		sender="0",
		recipient="For the miner",
		amount=1,
	)
	
	previous_hash = blockchain.compute_hash(last_block)
	block = blockchain.new_block(proof, previous_hash)

	response = {'message': 'Block mined!',
			'index': block['index'],
			'timestamp': block['timestamp'],
			'transactions': block['transactions'],
			'proof': block['proof'],
			'previous_hash': block['previous_hash']}
	return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def get_chain():
	response = {'chain': blockchain.chain,
				'length': len(blockchain.chain)}
	return jsonify(response), 200

app.run(host='127.0.0.1', port=5000)
