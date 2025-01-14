from typing import *
import msgpack


class IpcForward:
    """IPC转发消息"""

    def __init__(self, command: str, client_id: Optional[str] = None, data: Any = None):
        self.command = command
        self.client_id = client_id
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "command": self.command,
            "client_id": self.client_id,
            "data": self.data
        }

    @classmethod
    def from_data(cls, data: bytes) -> "IpcForward":
        """从字节数据创建实例"""
        try:
            unpacked = msgpack.unpackb(data)
            return cls(**unpacked)
        except Exception as e:
            raise ValueError(f"Invalid forward data: {e}")

    def __str__(self) -> str:
        return f"IpcForward(command={self.command}, client_id={self.client_id}, data={self.data})"
