from hashlib import sha256
from merkletools import MerkleTools
from time import time
from transaction import Transaction
from block import Block


class Blockchain:
    SECONDS_PER_BLOCK = 15

    def __init__(self):
        self.current_transactions = []
        self.chain = []

        self.new_block(nonce = 100, txs = self.current_transactions, prev_hash = 1)

        print(self.chain)

    def find_nonce(prev_hash, merkle_root):
        nonce = 0
        while self.is_valid_nonce(prev_hash, merkle_root, nonce) is False:
            nonce += 1

        return nonce

    @staticmethod
    def is_valid_nonce(prev_hash, merkle_root, nonce):
        guess = f'{prev_hash}{merkle_root}{nonce}'.encode()
        guess_hash = sha256(sha256(guess)).hexdigest()
        
        return guess_hash[:4] == "0000"

    def new_block(self, nonce, txs, prev_hash=None):
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
            nonce = self.find_nonce(sha256(self.chain[-1]).hexdigest(), mt.get_merkle_root()) # Nonceを見つける
        
        block = Block(
            prev_hash = prev_hash,
            height = len(self.chain),
            timestamp = time(),
            merkle_root = mt.get_merkle_root(),
            nonce = nonce,
            txs = txs
        )

        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, input, output, amount):
        """
        新しいトランザクションの生成
        """
        self.current_transactions.append(Transaction(input, output, amount))
        print(self.current_transactions)

    # def run(self):
    #     self.new_transaction('hoge', 'foo', 1000)


if __name__ == '__main__':
    Blockchain()
