import msgpack
from typing import *
from .header import IpcHeader


class IpcRequest:
    def __init__(self, id: str, clientId: str, path: str, header: "IpcHeader", body: Any):
        self.id = id
        self.clientId = clientId
        self.path = path
        self.header = header
        self.body = body

    @classmethod
    def from_data(cls, data: bytes):
        data = msgpack.unpackb(data)
        data = {**data, "header": IpcHeader(**data["header"])}
        return cls(**data)

    def __str__(self) -> str:
        return f"IpcRequest(id={self.id}, clientId={self.clientId}, path={self.path}, header={self.header}, body={self.body})"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "clientId": self.clientId,
            "path": self.path,
            "header": self.header.to_dict(),
            "body": self.body,
        }
