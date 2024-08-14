from typing import *


class IpcConfig:
    def __init__(self, sock: str, recv_limit: int = 1024):
        self.sock = sock  # sock 文件路径
        self.recv_limit = recv_limit  # 接收数据大小限制

    def update(self, *args, **kwargs):
        if len(args) == 1 and args[0] is None:
            return self
        if len(args) == 1 and isinstance(args[0], IpcConfig):
            return self.update(**args[0].to_dict())
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def to_dict(self):
        return {
            "sock": self.sock,
            "recv_limit": self.recv_limit,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @classmethod
    def new(cls, **kwargs):
        return cls.default().update(**kwargs)

    @classmethod
    def default(cls):
        config = {
            "sock": "/tmp/ipcserver.sock",
            "recv_limit": 1024 * 1024 * 50,  # 50MB
        }
        return cls.from_dict(config)
