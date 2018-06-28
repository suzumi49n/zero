# coding: UTF-8

class Block:
    # prev_hash = 0
    # height = 0
    # timestamp = 0
    # merkle_root = 0
    # nonce = 0
    # txs = []

    def __init__(self, prev_hash, height, timestamp, merkle_root, nonce, txs):
        self.prev_hash = prev_hash
        self.height = height
        self.timestamp = timestamp
        self.merkle_root = merkle_root
        self.nonce = nonce
        self.txs = txs

    def __repr__(self):
        return f"prev_hash={self.prev_hash} height={self.height} timestamp={self.timestamp} merkle_root={self.merkle_root} nonce={self.nonce} txs={self.txs}"

import json
class BlockJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Block): # Blockは'Block'としてエンコード
            return 'Block'
        return super(BlockJSONEncoder, self).default(o) # 他の型はdefaultのエンコード方式を使用