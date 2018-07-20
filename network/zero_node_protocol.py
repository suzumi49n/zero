import logging
import binascii
from core.helper import Helper
from twisted.internet import task
from twisted.internet.protocol import Protocol

logger = logging.getLogger(__name__)


class ZeroProtocol(Protocol):

    peer_info = None

    def __init__(self):
        from network.zeronode import ZeroNode

        self.zero_node = ZeroNode.Instance()
        self.node_id = self.zero_node.node_id
        self.endpoint = ''
        self.host = None
        self.port = None

    def disconnect(self):
        self.transport.loseConnection()

    def connectionMade(self):
        """
        接続が確立したときに呼び出される
        このノードにつながっているリモートノードの情報を取得
        :return:
        """
        self.endpoint = self.transport.getPeer()
        self.zero_node.add_connected_peer(self)
        self.dlog('Connection from %s' % self.endpoint)

    def dataReceived(self, data):
        print(f'data received: {data}')
        self.message_received(data)
        # logger.debug(f'data received: {data}')

    def message_received(self, msg=None):
        # if msg.command == 'getaddr':
        self.protocol_ready()

    def dlog(self, msg):
        print(f'[{self.node_id}] {self.node_id} - {msg}')
        # logger.debug('[%s] %s - %s' % (self.node_id, self.endpoint, msg))

    def request_peer_info(self):
        self.send_serialized_message('getaddr')

    def protocol_ready(self):
        """
        3分ごとに新しいノード情報を取得する
        """
        self.peer_info = task.LoopingCall(self.request_peer_info)
        self.peer_info.start(120)

    def send_serialized_message(self, msg):
        """
        リモートクライアントへメッセージを送る
        :param msg: string
        :return:
        """
        bin_array = Helper.to_array(msg)
        self.transport.write(bin_array)

    def send_message(self, data):
        # msg = binascii.b2a_hex(data.encode('utf-8'))
        # ba = binascii.unhexlify(msg)
        self.transport.write(data)
