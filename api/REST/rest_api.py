import sys
import json

from core.blockchain import Blockchain
from uuid import uuid4

from klein import Klein
from flask import Flask, jsonify, request

args = sys.argv
# app = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False
this_node_id = str(uuid4()).replace('-', '')

blockchain = Blockchain()


class RestApi:
    app = Klein()

    # トランザクションの追加
    @app.route('/transactions/new', methods=['POST'])
    def new_transactions(self, req):
        req.setHeader('Content-Type', 'application/json')
        payload = json.loads(req.content.read())
        required = ['input', 'output', 'amount']

        if not all(key in payload for key in required):
            return json.dumps({'message': 'Missing payloads'})

        blockchain.new_transaction(payload['input'], payload['output'], payload['amount'])

        res = {'message': 'トランザクションがブロックに追加されました'}

        return json.dumps(res, sort_keys=True)

    # フルブロックを取得する
    @app.route('/chain', methods=['GET'])
    def chain(self, req):
        req.setHeader('Content-Type', 'application/json')
        res = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain)
        }
        # return json.dumps(res, sort_keys=True)
        return json.dumps(res, sort_keys=True)

    # 今のトランザクションプールを取得
    @app.route('/tx_pool', methods=['GET'])
    def tx_pool(self, req):
        req.setHeader('Content-Type', 'application/json')
        res = {
            'tx_pool': blockchain.current_transactions
        }
        return json.dumps(res, sort_keys=True)

    # マイニング
    @app.route('/mine', methods=['GET'])
    def mining(self, req):
        req.setHeader('Content-Type', 'application/json')
        last_block = blockchain.last_block()

        # マイニング競争に勝ったユーザーに対するインセンティブ
        # マイニング報酬を表すためにinputは0にする
        blockchain.new_transaction(
            input="0",
            output=this_node_id,
            amount=100
        )

        blockchain.new_block(blockchain.current_transactions, blockchain.hash(last_block))

        res = {'message': 'ブロックが採掘されました'}
        return json.dumps(res, sort_keys=True)

    # ノードの登録
    @app.route('/nodes/register', methods=['POST'])
    def register_node(self, req):
        req.setHeader('Content-Type', 'application/json')
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
        return json.dumps(response, sort_keys=True)

    # 最長チェーンの同期
    @app.route('/nodes/resolve', methods=['GET'])
    def consensus(self, req):
        req.setHeader('Content-Type', 'application/json')
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

        return json.dumps(response, sort_keys=True)
