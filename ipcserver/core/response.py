from enum import IntEnum
from typing import *
from colorama import Fore
import msgpack
if TYPE_CHECKING:
    from .request import IpcRequest


class IpcStatus(IntEnum):
    OK = 200
    CACHED = 304
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502


class ResponseType(IntEnum):
    RequestReply = 0  # 针对 request 的回复
    Active = 1  # 主动推送


DataType = Union[Dict, List, None]


def truncate_and_serialize(data: DataType, max_size=10):
    if isinstance(data, str):
        if len(data) > max_size:
            return data[:max_size] + "..."
        else:
            return data
    elif isinstance(data, (list, tuple)):
        return [truncate_and_serialize(item, max_size) for item in data]
    elif isinstance(data, dict):
        return {k: truncate_and_serialize(v, max_size) for k, v in data.items()}
    elif data is None:
        return data
    else:
        return str(data)


class IpcResponse:
    def __init__(self, code: IpcStatus = None, message: str = None, data: DataType = None):
        assert code is not None, "状态码不能为None"
        self.data = data
        self.code = code
        self.message = message

    def to_dict(self) -> Dict:
        return {"data": self.data, "code": self.code, "message": self.message}

    def to_bytes(self) -> bytes:
        return msgpack.packb(self.to_dict())

    def is_normal(self):
        """返回状态是否正常"""
        return 200 <= self.code < 300 or self.code == 304

    def get_code(self):
        """状态码 (IpcStatus, 是服务器约定的, 不是Ipc协议约定的)"""
        return self.code

    def get_data(self):
        """反馈数据"""
        return self.data

    @classmethod
    def make_bytes(cls, request: "IpcRequest", response: "IpcResponse") -> bytes:
        return msgpack.packb([request.to_dict(), response.to_dict()])

    @classmethod
    def ok(cls, data: DataType = None, message: str = "处理成功", code=IpcStatus.OK):
        return cls(data=data, code=code, message=message)

    @classmethod
    def error(
        cls, data: DataType = None, message: str = "处理失败", code=IpcStatus.BAD_REQUEST
    ):
        return cls(data=data, code=code, message=message)

    def __str__(self):

        max_length = (
            50 if self.is_normal() else len(self.message)
        )  # 请求正常则最多显示50字符, 否则显示完整错误信息
        suffix = ""
        if len(self.message) > max_length:
            suffix = "..."
        message = self.message[:max_length] + suffix  # 超出 max_length 的部分省略
        begin = None
        if self.is_normal():
            begin = Fore.GREEN
        else:
            begin = Fore.RED
        end = Fore.RESET
        return (
            begin
            + f"IpcResponse(code={self.code}, message={message}, data={truncate_and_serialize(self.data, max_size=200)})"
            + end
        )
