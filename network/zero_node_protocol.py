import logging
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
