class ReadStreamError(Exception):
    pass


class StreamNotFoundError(ReadStreamError):
    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        message = f"Stream not found: {self.stream_name}"
        super().__init__(message)
