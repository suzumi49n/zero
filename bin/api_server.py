import argparse
from twisted.internet import reactor, endpoints
from twisted.web.server import Site

from api.REST.rest_api import RestApi


def main():
    """
    非推奨
    """
    parser = argparse.ArgumentParser()

    # Ports for RPC and REST api
    group_modes = parser.add_argument_group(title="Mode(s)")
    group_modes.add_argument("--port-rpc", type=int, help="port to use for the json-rpc api (eg. 10332)")
    group_modes.add_argument("--port-rest", type=int, help="port to use for the rest api (eg. 80)")

    parser.add_argument("--host", action="store", type=str, help="Hostname (for example 127.0.0.1)", default="0.0.0.0")
    args = parser.parse_args()

    if not args.port_rpc and not args.port_rest:
        print("Error: specify at least one of --port-rpc / --port-rest")
        parser.print_help()
        return

    reactor.suggestThreadPoolSize(15)
    api_server_rest = RestApi()
    endpoint_rest = 'tcp:port={0}:interface={1}'.format(args.port_rest, args.host)
    endpoints.serverFromString(reactor, endpoint_rest).listen(Site(api_server_rest.app.resource()))

    reactor.run()


if __name__ == "__main__":
    main()
