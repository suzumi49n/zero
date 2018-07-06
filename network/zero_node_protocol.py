import logging
from twisted.internet.protocol import Protocol

logger = logging.getLogger(__name__)

class ZeroProtocol(Protocol):

    def dataReceived(self, data):
        logger.debug(f'data received: {data}')