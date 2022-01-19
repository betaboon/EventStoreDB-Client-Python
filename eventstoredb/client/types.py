from dataclasses import dataclass


@dataclass
class ClientOptions:
    host: str
    port: int = 2113
