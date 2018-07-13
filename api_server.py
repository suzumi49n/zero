import argparse
import logging

from twisted.internet import reactor, endpoints
from twisted.web.server import Site

from network.zeronode import ZeroNode, ZeroNodeClient
from api.REST.rest_api import RestApi
from config import config

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()

    # Ports for RPC and REST api
    group_modes = parser.add_argument_group(title="Mode(s)")
    group_modes.add_argument("--port-rpc", type=int, help="port to use for the json-rpc api (eg. 10332)")
    group_modes.add_argument("--port-rest", type=int, help="port to use for the rest api (eg. 80)")
    group_modes.add_argument("--port-tcp", type=int, help="port to use for the TCP (eg. 10082)")

    parser.add_argument("--host", action="store", type=str, help="Hostname (for example 127.0.0.1)", default="0.0.0.0")
    args = parser.parse_args()

    # Setup network config
    config.setup_mainnet()

    # Setup twisted reactor
    reactor.suggestThreadPoolSize(15)
    ZeroNode.Instance().start()

    if not args.port_rpc and not args.port_rest:
        print("Error: specify at least one of --port-rpc / --port-rest")
        parser.print_help()
        return

    if args.port_rest:
        print(f'Starting REST api server on http://{args.host}:{args.port_rest}')
        # logger.info("Starting REST api server on http://%s:%s" % (args.host, args.port_rest))
        api_server_rest = RestApi()
        endpoint_rest = 'tcp:port={0}:interface={1}'.format(args.port_rest, args.host)
        endpoints.serverFromString(reactor, endpoint_rest).listen(Site(api_server_rest.app.resource()))
        # reactor.listenTCP(int(args.port_rest), Site(api_server_rest.app.resource()))


    # ZeroNode.Instance().send()
    # TCP server
    reactor.listenTCP(int(args.port_tcp), ZeroNodeClient())
    reactor.run()

    ZeroNode.Instance().shutdown()


if __name__ == "__main__":
    main()
