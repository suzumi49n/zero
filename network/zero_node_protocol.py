import logging
import binascii
from twisted.internet.protocol import Protocol

logger = logging.getLogger(__name__)


class ZeroProtocol(Protocol):

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
        self.dlog('Connection from %s' % self.endpoint)

    def dataReceived(self, data):
        print(f'data received: {data}')
        # logger.debug(f'data received: {data}')

    def dlog(self, msg):
        print(f'[{self.node_id}] {self.node_id} - {msg}')
        # logger.debug('[%s] %s - %s' % (self.node_id, self.endpoint, msg))

    def send_message(self, data):
        # msg = binascii.b2a_hex(data.encode('utf-8'))
        # ba = binascii.unhexlify(msg)
        self.transport.write(data)
