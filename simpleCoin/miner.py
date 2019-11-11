import time
import hashlib
import json
import requests
import base64
from flask import Flask, request
from multiprocessing import Process, Pipe
import ecdsa
import codecs
import elgamal
from utils import *
from miner_config import MINER_ADDRESS, MINER_NODE_URL, PEER_NODES
import os
    
node = Flask(__name__)

PUBLIC_KEY_SIZE = 25


class Block:
    def __init__(self, index, timestamp, data, next_public, previous_private=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.body_hash = self.body_hash() 
        self.next_public = next_public
        self.previous_private = previous_private

    def hash_header(self):
        sha = hashlib.sha256()
        sha.update((str(self.index)+str(self.timestamp)+str(self.body_hash)+str(self.previous_private)+str(self.next_public)).encode('utf-8'))
        return sha.hexdigest()

    def body_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.data).encode('utf-8'))
        return sha.hexdigest()
        

def create_genesis_block():
    cipher = elgamal.generate_keys(seed=0xffffffffffffff,iNumBits=PUBLIC_KEY_SIZE)
    return Block(0, time.time(), {"transactions": None}, cipher)


def create_second_block():
    cipher = elgamal.generate_keys(seed=int(BLOCKCHAIN[0].hash_header(), 16),iNumBits = PUBLIC_KEY_SIZE)
    return Block(1, time.time(), {"transactions": None}, cipher)

# Node's blockchain copy
BLOCKCHAIN = [create_genesis_block()]
BLOCKCHAIN.append(create_second_block())
""" Stores the transactions that this node has in a list.
If the node you sent the transaction adds a block
it will get accepted, but there is a chance it gets
discarded and your transaction goes back as if it was never
processed"""
NODE_PENDING_TRANSACTIONS = []


# TODO publicKey 를 받아 쌍이 되는 개인키를 찾는 함수.
# 만약, 다른 노드가 먼저 발견하게 되면 False 를 반환한다.
def proof_of_work(pub, blockchain):
    i=0
    start_time = time.time()
    while True:
        if pub.h == elgamal.modexp(pub.g,i,pub.p) :
            before_private = elgamal.PrivateKey(pub.p,pub.g,i,pub.iNumBits)
            break
    
        if (time.time()-start_time) > 30:
            start_time = time.time()
            # If any other node got the proof, stop searching
            new_blockchain = consensus(blockchain)
            if new_blockchain:
                # (False: another node got proof first, new blockchain)
                return False, new_blockchain
                # Once that number is found, we can return it as a proof of our work            
        i = i+1
    return before_private, blockchain


def mine(a, blockchain, node_pending_transactions):
    BLOCKCHAIN = blockchain
    NODE_PENDING_TRANSACTIONS = node_pending_transactions
    while True:
        """Mining is the only way that new coins can be created.
        In order to prevent too many coins to be created, the process
        is slowed down by a proof of work algorithm.
        """
        # Get the last proof of work
        last_block = BLOCKCHAIN[-2]
        last_public = last_block.next_public
        # Find the proof of work for the current block being mined
        # Note: The program will hang here until a new proof of work is found
        proof = proof_of_work(last_public, BLOCKCHAIN)
        # If we didn't guess the proof, start mining again
        if not proof[0]:
            # Update blockchain and save it to file
            BLOCKCHAIN = proof[1]
            a.send(BLOCKCHAIN)
            continue
        else:
            # Once we find a valid proof of work, we know we can mine a block so
            # ...we reward the miner by adding a transaction
            # First we load all pending transactions sent to the node server
            NODE_PENDING_TRANSACTIONS = requests.get(MINER_NODE_URL + "/txion?update=" + MINER_ADDRESS).content
            NODE_PENDING_TRANSACTIONS = json.loads(NODE_PENDING_TRANSACTIONS)
        
            # Then we add the mining reward
            NODE_PENDING_TRANSACTIONS.append({
                "from": "network",
                "to": MINER_ADDRESS,
                "amount": 1})
            # Now we can gather the data needed to create the new block
            
            new_block_data = {
                "transactions": list(NODE_PENDING_TRANSACTIONS)
            }
            
            new_block_index = last_block.index + 2
            new_block_timestamp = time.time()
            before_hash = BLOCKCHAIN[-1].hash_header()
            cipher = elgamal.generate_keys(iNumBits=PUBLIC_KEY_SIZE, seed=int(before_hash, 16))
            new_block_next_public = cipher

            # Empty transaction list
            NODE_PENDING_TRANSACTIONS = []

            # Now create the new block                    
            mined_block = Block(new_block_index, new_block_timestamp, new_block_data, new_block_next_public, proof[0])
            BLOCKCHAIN.append(mined_block)
            # print("before_public_key = " + str(proof[0].key.p * proof[0].key.q))
            print(json.dumps({
                "index": mined_block.index,
                "timestamp": str(mined_block.timestamp),
                "body_hash": str(int(mined_block.body_hash, 16)),
                "next_public": str(hex(mined_block.next_public.g)) + ", " + str(hex(mined_block.next_public.h)),
                "previous_private": str(hex(mined_block.previous_private.x)),
                "data": mined_block.data
            }, indent=4) + "\n")
            a.send(BLOCKCHAIN)
            requests.get(MINER_NODE_URL + "/blocks?update=" + MINER_ADDRESS)
            

def find_new_chains():
    # Get the blockchains of every other node
    other_chains = []
    for node_url in PEER_NODES:
        # Get their chains using a GET request
        block = requests.get(node_url + "/blocks").content
        # Convert the JSON object to a Python dictionary
        block = json.loads(block)
        # Verify other node block is correct
        validated = validate_blockchain(block)
        if validated:
            # Add it to our list
            other_chains.append(block)
    return other_chains


def consensus(blockchain):
    # Get the blocks from other nodes
    other_chains = find_new_chains()
    # If our chain isn't longest, then we store the longest chain
    BLOCKCHAIN = blockchain
    longest_chain = BLOCKCHAIN
    for chain in other_chains:
        if len(longest_chain) < len(chain):
            longest_chain = chain
    # If the longest chain wasn't ours, then we set our chain to the longest
    if longest_chain == BLOCKCHAIN:
        # Keep searching for proof
        return False
    else:
        # Give up searching proof, update chain and start over again
        BLOCKCHAIN = longest_chain
        return BLOCKCHAIN


def validate_blockchain(block):
    """Validate the submitted chain. If hashes are not correct, rULrd9xIYYgm5D1yUHAj9axyrib0R3chDnJJ2lDiKIwCFFAFYWrkXU7sPWY4RLccMcOQQ+KDvPuOxrlkl0Y+1hw==32
    eturn false
    block(str): json
    """
    return True


@node.route('/blocks', methods=['GET'])
def get_blocks():
    # Load current blockchain. Only you should update your blockchain
    if request.args.get("update") == MINER_ADDRESS:
        global BLOCKCHAIN
        BLOCKCHAIN = b.recv()
    chain_to_send = BLOCKCHAIN
    # Converts our blocks into dictionaries so we can send them as json objects later
    chain_to_send_json = []
    for block in chain_to_send:
        block = {
            "index": str(block.index),
            "timestamp": str(block.timestamp),
            "body_hash": str(block.body_hash),
            "next_public": "( " + str(hex(block.next_public.g)) + ", " + str(hex(block.next_public.h)) + ", " + str(hex(block.next_public.p)) +" )",
            "previous_private": "( " + str(hex(block.previous_private.x)) + " )" if block.previous_private else None,
            "data": block.data
        }
        chain_to_send_json.append(block)

    chain_to_send = json.dumps(chain_to_send_json)
    return chain_to_send
    # Send our chain to whomever requested it


@node.route('/txion', methods=['GET', 'POST'])
def transaction():
    """Each transaction sent to this node gets validated and submitted.
    Then it waits to be added to the blockchain. Transactions only move
    coins, they don't create it.
    """
    if request.method == 'POST':
        # On each new POST request, we extract the transaction data
        new_txion = request.get_json()
        # Then we add the transaction to our list
        if validate_signature(new_txion['from'], new_txion['signature'], new_txion['message']):
            NODE_PENDING_TRANSACTIONS.append(new_txion)
            # Because the transaction was successfully
            # submitted, we log it to our console
            print("New transaction")
            print("FROM: {0}".format(new_txion['from']))
            print("TO: {0}".format(new_txion['to']))
            print("AMOUNT: {0}\n".format(new_txion['amount']))
            # Then we let the client know it worked out
            return "Transaction submission successful\n"
        else:
            return "Transaction submission failed. Wrong signature\n"
    # Send pending transactions to the mining process
    elif request.method == 'GET' and request.args.get("update") == MINER_ADDRESS:
        pending = json.dumps(NODE_PENDING_TRANSACTIONS)
        # Empty transaction list
        NODE_PENDING_TRANSACTIONS[:] = []
        return pending


def validate_signature(public_key, signature, message):
    """Verifies if the signature is correct. This is used to prove
    it's you (and not someone else) trying to do a transaction with your
    address. Called when a user tries to submit a new transaction.
    """
    public_key = (base64.b64decode(public_key)).hex()
    signature = base64.b64decode(signature)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
    # Try changing into an if/else statement as except is too broad.
    try:
        return vk.verify(signature, message.encode())
    except:
        return False


def welcome_msg():
    print("""       =========================================\n
        SIMPLE COIN v1.0.0 - BLOCKCHAIN SYSTEM\n
       =========================================\n\n
        You can find more help at: https://github.com/cosme12/SimpleCoin\n
        Make sure you are using the latest version or you may end in
        a parallel chain.\n\n\n""")


if __name__ == '__main__':
    welcome_msg()
    # Start mining
    a, b = Pipe()
    p1 = Process(target=mine, args=(a, BLOCKCHAIN, NODE_PENDING_TRANSACTIONS))
    p1.start()
    # Start server to receive transactions
    p2 = Process(target=node.run(), args=b)
    p2.start()
