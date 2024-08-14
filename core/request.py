import msgpack
from typing import *
from .header import Header


class IpcRequest:
    def __init__(self, header: "Header", body: Any):
        self.header = header
        self.body = body

    @classmethod
    def from_data(cls, data: bytes):
        [path, header, body] = msgpack.unpackb(data)
        header = Header(path=path, **header)
        return cls(header=header, body=body)

    def __str__(self) -> str:
        return f"IpcRequest(header={self.header}, body={self.body})"
