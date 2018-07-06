from hashlib import sha256
import sys
import json
import requests

from urllib.parse import urlparse
from uuid import uuid4
from time import time
# from core.transaction import Transaction
from network.zeronode import ZeroNodeClient
# from core.block import Block, BlockJSONEncoder
from twisted.internet import reactor

from flask import Flask, jsonify, request
from merkletools import MerkleTools

# ブロックの生成時間間隔(秒)
SECONDS_PER_BLOCK = 15
# ブロックハッシュ値の先頭桁数の指定
TARGET_NONCE_ZERO_DIGIT = 5


class Blockchain:

    # ジェネシスブロック生成
    def __init__(self):
        # reactor.connectTCP('127.0.0.1', 4001, ZeroNodeClient())
        # reactor.run()

        self.current_transactions = []
        self.chain = []
        # ノードリスト
        self.nodes = set()

        self.new_block(txs=self.current_transactions, prev_hash=1)


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
        print(mt.get_leaf_count())  # トランザクションの数

        mt.make_tree()  # マークルツリーの生成

        if not self.chain:
            nonce = 1
            print("created Genesis Block")
        else:
            block_buffer = json.dumps(self.chain[-1]).encode()
            nonce = self.find_nonce(
                sha256(block_buffer).hexdigest(),
                mt.get_merkle_root()
            )  # Nonceを見つける

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
