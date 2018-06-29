from hashlib import sha256
import sys
import json
import requests

from urllib.parse import urlparse
from uuid import uuid4
from time import time
from transaction import Transaction
from block import Block, BlockJSONEncoder

from flask import Flask, jsonify, request
from merkletools import MerkleTools

# ブロックの生成時間間隔(秒)
SECONDS_PER_BLOCK = 15
# ブロックハッシュ値の先頭桁数の指定
TARGET_NONCE_ZERO_DIGIT = 5

class Blockchain:

    # ジェネシスブロック生成
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        # ノードリスト
        self.nodes = set()

        self.new_block(txs = self.current_transactions, prev_hash = 1)

        print(self.chain)

    def find_nonce(self, prev_hash, merkle_root):
        nonce = 0
        while self.is_valid_nonce(prev_hash, merkle_root, nonce) is False:
            nonce += 1

        return nonce

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        ブロックチェーンがが正しいか確認する

        :param chain: <list> ブロックチェーン
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # ブロックのハッシュが正しいか
            if block['prev_hash'] != self.hash(last_block):
                return False

            # nonceが正しいか
            # if not self.is_valid_nonce(last_block['nonce'], block['nonce']):
            #     return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        ネットワークで最も長いチェーンを採用する
        TODO: ブロードキャストされたチェーンを検証し、それを正にする処理に変更する
        """
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            res = requests.get(f'http://{node}/chain')

            if res.status_code == 200:
                length = res.json()['length']
                chain = res.json()['chain']

                # チェーンが有効かつ最も長いかを確認
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # 自分のチェーンより長く、かつ有効なチェーンだった場合そのチェーンを採用する
        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def is_valid_nonce(prev_hash, merkle_root, nonce):
        """
        ブロックハッシュが正しくなるnonceか
        :param prev_hash: 前のブロックのハッシュ
        :param merkle_root: トランザクションのマークルルート
        :param nonce: 求める値
        """
        guess = f'{prev_hash}{merkle_root}{nonce}'.encode()
        guess_hash = sha256(guess).hexdigest()
        
        return guess_hash[:TARGET_NONCE_ZERO_DIGIT] == ''.zfill(TARGET_NONCE_ZERO_DIGIT)

    @staticmethod
    def hash(block):
        """
        ブロックのSHA-256ハッシュを生成
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()


    def new_block(self, txs, prev_hash=None):
        """
        新しいブロックの生成
        """
        nonce = 0
        mt = MerkleTools()
        mt.add_leaf(txs, True)
        print(mt.get_leaf_count()) #トランザクションの数

        mt.make_tree() # マークルツリーの生成

        if not self.chain:
            nonce = 1
            print("created Genesis Block")
        else:
            block_buffer = json.dumps(self.chain[-1]).encode()
            nonce = self.find_nonce(
                sha256(block_buffer).hexdigest(),
                mt.get_merkle_root()
            ) # Nonceを見つける
        
        block = {
            'prev_hash': prev_hash,
            'height': len(self.chain),
            'timestamp': time(),
            'merkle_root': mt.get_merkle_root(),
            'nonce': nonce,
            'txs': txs
        }

        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, input, output, amount):
        """
        新しいトランザクションの生成
        トランザクションプールにappendされる
        """
        rawTx = {
            'input': input,
            'output': output,
            'amount': amount
            }
            
        hashedTx = sha256(json.dumps(rawTx).encode()).hexdigest()
        self.current_transactions.append(hashedTx)
        print(f'NewTransaction={self.current_transactions}')
        
    def last_block(self):
        return self.chain[-1]

    # def run(self):
    #     self.new_transaction('hoge', 'foo', 1000)

args = sys.argv
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
this_node_id = str(uuid4()).replace('-', '')

blockchain = Blockchain()

# トランザクションの追加
@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    payload = request.get_json()
    required = ['input', 'output', 'amount']

    if not all(key in payload for key in required):
        return 'Missing payloads', 400

    blockchain.new_transaction(payload['input'], payload['output'], payload['amount'])

    res = {'message': 'トランザクションがブロックに追加されました'}

    return jsonify(res), 200

# フルブロックを取得する
@app.route('/chain', methods=['GET'])
def chain():
    res = {
       'chain': blockchain.chain,
       'length': len(blockchain.chain) 
    }
    return jsonify(res), 200

# 今のトランザクションプールを取得
@app.route('/tx_pool', methods=['GET'])
def tx_pool():
    res = {
        'tx_pool': blockchain.current_transactions
    }
    return jsonify(res), 200

# マイニング
@app.route('/mine', methods=['GET'])
def mining():
    last_block = blockchain.last_block()
    
    # マイニング競争に勝ったユーザーに対するインセンティブ
    # マイニング報酬を表すためにinputは0にする
    blockchain.new_transaction(
        input = "0",
        output = this_node_id,
        amount = 100
    )
    
    blockchain.new_block(blockchain.current_transactions, blockchain.hash(last_block))

    res = {'message': 'ブロックが採掘されました'}
    return jsonify(res), 200

# ノードの登録
@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: 有効ではないノードのリストです", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': '新しいノードが追加されました',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

# 最長チェーンの同期
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'チェーンが置き換えられました',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'チェーンが確認されました',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    port = args[1]
    app.run(host="0.0.0.0", port=port)
    # Blockchain()
