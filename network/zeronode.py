import logging
import random
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor

from network.zero_node_protocol import ZeroProtocol
from config import config

logger = logging.getLogger(__name__)


# 接続処理をするクラス
class ZeroNodeClient(ReconnectingClientFactory):
    protocol = ZeroProtocol

    def buildProtocol(self, addr):
        """
        Protocolクラスのインスタンス生成
        """
        print(f'Successfully connected to {addr}')

        self.resetDelay()  # retry delayを元に戻す

        protocol = self.protocol()
        protocol.factory = self
        return protocol

    def startedConnecting(self, connector):
        """
        接続後に呼び出される
        """
        print('Started to connect.')
        # logger.info(u'Started to connect.')

    def clientConnectionLost(self, connector, reason):
        """
        接続を失った際のハンドラ
        """
        print(f'Lost connection. Reason: {reason}')
        # logger.warning(u'Lost connection. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        """
        接続に失敗した際のハンドラ
        """
        print(f'Connection failed. Reason: {reason}')
        # logger.error(u'Connection failed. Reason: %s' % reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


class ZeroNode:
    Peers = []
    ADDR = []
    __LEAD = None
    node_id = None

    @staticmethod
    def Instance():
        if ZeroNode.__LEAD is None:
            ZeroNode.__LEAD = ZeroNode()
        return ZeroNode.__LEAD

    def __init__(self):
        self.setup()

    def setup(self):
        self.Peers = []
        self.ADDR = []
        self.node_id = random.randint(1294967200, 4294967200)

    def add_connected_peer(self, peer):
        if peer not in self.Peers:
            if len(self.Peers) < config.CONNECTED_MAX_PEER:
                self.Peers.append(peer)
            else:
                if peer.Address in self.ADDR:
                    self.ADDR.remove(peer.Address)
                peer.disconnect()

    def setup_connection(self, host, port):
        if len(self.Peers) < config.CONNECTED_MAX_PEER:
            reactor.connectTCP(host, int(port), ZeroNodeClient())
            print('### 繋がった')

    def start(self):
        start_delay = 0
        print('#### start()')
        for bootstrap in config.SEED_LIST:
            host, port = bootstrap.split(':')
            self.ADDR.append('%s:%s' % (host, port))
            reactor.callLater(start_delay, self.setup_connection, host, port)
            start_delay += 1

    def remote_node_peer_received(self, host, port, index):
        addr = '%s:%s' % (host, port)
        if addr not in self.ADDRS and len(self.Peers) < config.CONNECTED_PEER_MAX:
            self.ADDRS.append(addr)
            reactor.callLater(index * 10, self.SetupConnection, host, port)

    def start_server(self, port):
        reactor.listenTCP(port, ZeroNodeClient())

    def shutdown(self):
        for p in self.Peers:
            p.disconnect()

    def send(self):
        for p in self.Peers:
            p.send_message('こんにちは')
