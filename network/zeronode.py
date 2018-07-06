import logging
from twisted.internet.protocol import ReconnectingClientFactory

from network.zero_node_protocol import ZeroProtocol

logger = logging.getLogger(__name__)


# 接続処理をするクラス
class ZeroNodeClient(ReconnectingClientFactory):
    protocol = ZeroProtocol

    def buildProtocol(self, addr):
        """
        Protocolクラスのインスタンス生成
        """
        logging.info(u'Successfully connected to %s' % addr)

        self.resetDelay()  # retry delayを元に戻す

        protocol = self.protocol()
        protocol.factory = self
        return protocol

    def startedConnecting(self, connector):
        """
        接続後に呼び出される
        """
        logger.info(u'Started to connect.')

    def clientConnectionLost(self, connector, reason):
        """
        接続を失った際のハンドラ
        """
        logger.warning(u'Lost connection. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        """
        接続に失敗した際のハンドラ
        """
        logger.error(u'Connection failed. Reason: %s' % reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
