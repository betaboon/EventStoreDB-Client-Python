from grpclib.client import Channel

from eventstoredb.client.types import ClientOptions


class Client:
    def __init__(self, options: ClientOptions) -> None:
        self.channel = Channel(host=options.host, port=options.port)
