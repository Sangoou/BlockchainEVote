import time
import hashlib
import json
import requests
import base64
from flask import Flask, request
from multiprocessing import Process, Pipe
import ecdsa
# import codecs
import elgamal
from miner_config import MINER_ADDRESS, MINER_NODE_URL, PEER_NODES
from typing import Optional

# import os

node = Flask(__name__)

# Variables that will determine how soon it will be released
time_ = 30
flag_ = 0
# How many blocks to adjust the public key size (difficulty level)
term = 5
start_time = 0


class Block:
    def __init__(self, index, timestamp, data, next_public, public_key_size, nonce=None, before_header_hash=None):
        self.version = 1.0
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.difficult = next_public.p
        self.before_header_hash = before_header_hash
        self.nonce = nonce
        self.public_key_size = public_key_size
        self.next_public = next_public

    def hash_header(self):
        sha = hashlib.sha256()
        sha.update(
            (str(self.index) + str(self.timestamp) + str(self.body_hash) + str(self.next_public)).encode('utf-8') + str(
                self.nonce).encode('utf-8'))
        return sha.hexdigest()

    def body_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.data).encode('utf-8'))
        return sha.hexdigest()


def create_genesis_block():
    cipher = elgamal.generate_keys(seed=0xffffffffffffff, i_num_bits=18)
    return Block(0, time.time(), {"transactions": None}, cipher, 18)


# Node's blockchain copy
BLOCKCHAIN = [create_genesis_block()]

""" Stores the transactions that this node has in a list.
If the node you sent the transaction adds a block
it will get accepted, but there is a chance it gets
discarded and your transaction goes back as if it was never
processed"""
NODE_PENDING_TRANSACTIONS = []


def calculate_difficulty(difficulty):
    global flag_, start_time, time_

    if flag_ == 0:
        start_time = time.time()
        flag_ = 1

    else:
        if time.time() - start_time > time_:
            difficulty = difficulty - 1

        elif time.time() - start_time < time_:
            difficulty = difficulty + 1

        start_time = time.time()

    return difficulty


# TODO publicKey A function to find the paired private key by taking.
# If other nodes are found first, False is returned..

def proof_of_work(last_block, candidate_block: Block, blockchain) -> tuple[Optional[Block], list[Block]]:
    i = 0
    init_time = time.time()
    while True:
        candidate_block.nonce = i

        hash_header = int(candidate_block.hash_header(), last_block.public_key_size) % (last_block.difficult - 1) + 1

        if last_block.next_public.h == elgamal.mod_exp(last_block.next_public.g, hash_header, last_block.next_public.p):
            break

        if (time.time() - init_time) > 30:
            init_time = time.time()
            new_blockchain = consensus(blockchain)
            if new_blockchain:
                return None, new_blockchain
        i = i + 1
    return candidate_block, blockchain


def mine(connection,
         blockchain: list[Block],
         node_pending_transactions):
    # declare with global keyword to modify blockchain and pending transactions
    global BLOCKCHAIN, NODE_PENDING_TRANSACTIONS
    BLOCKCHAIN = blockchain
    NODE_PENDING_TRANSACTIONS = node_pending_transactions

    while True:
        """Mining is the only way that new coins can be created.
        In order to prevent too many coins to be created, the process
        is slowed down by a proof of work algorithm.
        """
        # Get the last proof of work
        last_block = blockchain[-1]
        difficulty = 1
        if last_block.index == 0:
            time.sleep(1)

        if (last_block.index + 2) % term == 2:
            difficulty = calculate_difficulty(last_block.public_key_size)

        NODE_PENDING_TRANSACTIONS = requests.get(MINER_NODE_URL + "/txion?update=" + MINER_ADDRESS).content
        NODE_PENDING_TRANSACTIONS = json.loads(NODE_PENDING_TRANSACTIONS)
        NODE_PENDING_TRANSACTIONS.append({"from": "network", "to": MINER_ADDRESS, "amount": 1})
        new_block_data = {"transactions": list(NODE_PENDING_TRANSACTIONS)}

        new_block_index = last_block.index + 2
        new_block_timestamp = time.time()
        before_header_hash_ = blockchain[-1].hash_header()
        before_public = blockchain[-1].next_public
        cipher = elgamal.generate_keys(i_num_bits=difficulty,
                                       seed=int(before_public.p + before_public.g + before_public.h))
        new_block_next_public = cipher
        candidate_block = Block(new_block_index, new_block_timestamp, new_block_data, new_block_next_public, difficulty,
                                before_header_hash=before_header_hash_)

        # Find the proof of work for the current block being mined
        # Note: The program will hang here until a new proof of work is found
        proof = proof_of_work(last_block, candidate_block, blockchain)
        # If we didn't guess the proof, start mining again
        if not proof[0]:
            # Update blockchain and save it to file
            blockchain = proof[1]
            connection.send(blockchain)
            continue
        else:
            # Once we find a valid proof of work, we know we can mine a block so
            # ...we reward the miner by adding a transaction
            # First we load all pending transactions sent to the node server

            '''
            # Then we add the mining reward
            NODE_PENDING_TRANSACTIONS.append({
                "from": "network",
                "to": MINER_ADDRESS,
                "amount": 1})
            # Now we can gather the data needed to create the new block
            '''
            # Empty transaction list

            NODE_PENDING_TRANSACTIONS = []
            # Now create the new block                    
            blockchain.append(proof[0])
            # print("before_public_key = " + str(proof[0].key.p * proof[0].key.q))
            print(json.dumps({
                "index": str(proof[0].index),
                "timestamp": str(proof[0].timestamp),
                "header_hash": str(proof[0].hash_header()),
                "difficult": str(proof[0].difficult),
                "public_key_size": str(proof[0].public_key_size),
                "before_header_hash": str(proof[0].before_header_hash),
                "next_public": "( " + str(hex(proof[0].next_public.g)) + ", " + str(
                    hex(proof[0].next_public.h)) + ", " + str(hex(proof[0].next_public.p)) + " )",
                "nonce": "( " + str(proof[0].nonce) + " )",
                "data": proof[0].data
            }, indent=4) + "\n")
            connection.send(blockchain)
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


def consensus(blockchain) -> Optional[list[Block]]:
    global BLOCKCHAIN
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
        return None
    else:
        # Give up searching proof, update chain and start over again
        BLOCKCHAIN = longest_chain
        return BLOCKCHAIN


def validate_blockchain(block):
    """Validate the submitted chain. If hashes are not correct,
    rULrd9xIYYgm5D1yUHAj9axyrib0R3chDnJJ2lDiKIwCFFAFYWrkXU7sPWY4RLccMcOQQ+KDvPuOxrlkl0Y+1hw==32
    return false
    block(str): json
    """
    return True


@node.route('/blocks', methods=['GET'])
def get_blocks():
    # Load current blockchain. Only you should update your blockchain
    BLOCKCHAIN = []
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
            "difficult": str(block.difficult),
            "public_key_size": str(block.public_key_size),
            "before_header_hash": str(block.before_header_hash),
            "next_public": "( " + str(hex(block.next_public.g)) + ", " + str(hex(block.next_public.h)) + ", " + str(
                hex(block.next_public.p)) + " )",
            "nonce": "( " + str(block.nonce) + " )",
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
    except ecdsa.BadSignatureError:
        print(f"Signature {signature} is not valid!")
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
    p2 = Process(target=node.run(), args=(b,))
    p2.start()
