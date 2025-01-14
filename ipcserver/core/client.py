import asyncio
import uuid
import msgpack
import socket
from typing import *
from .request import IpcRequest
from .response import IpcResponse
from .header import IpcHeader
from ..utils import Console


class IpcClient:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.client_id = str(uuid.uuid4())
        self.listeners: Dict[str, List[Callable]] = {}

    @classmethod
    async def connect(cls, sock: str) -> "IpcClient":
        """连接到IPC服务器"""
        try:
            reader, writer = await asyncio.open_unix_connection(sock)
            return cls(reader, writer)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to IPC server: {e}")

    def get_client_id(self) -> str:
        """获取客户端ID"""
        return self.client_id

    async def _send_message(self, data: bytes) -> None:
        """发送消息到服务器"""
        try:
            # 构造完整消息：8字节长度 + 数据内容
            message = len(data).to_bytes(8, byteorder='big') + data
            self.writer.write(message)
            await self.writer.drain()
        except Exception as e:
            raise ConnectionError(f"Failed to send message: {e}")

    async def _recv_message(self) -> bytes:
        """从服务器接收消息"""
        try:
            data = await self.reader.read(65536)
            if not data:
                raise ConnectionError("Connection closed by server")
            return data
        except Exception as e:
            raise ConnectionError(f"Error receiving message: {e}")

    async def send(self, path: str, data: Any = None) -> IpcResponse:
        """向指定路由发送数据并接收响应"""
        try:
            # 创建并发送请求
            request = IpcRequest(
                id=str(uuid.uuid4()),
                clientId=self.client_id,
                path=path,
                header=IpcHeader(compress=False),
                body=data
            )
            await self._send_message(msgpack.packb(request.to_dict(), use_bin_type=True))

            # 接收并解析响应
            response_data = await self._recv_message()
            if not response_data:
                raise ConnectionError("Connection closed by server")

            try:
                [req_dict, resp_dict] = msgpack.unpackb(
                    response_data, raw=False)
                response = IpcResponse(**resp_dict)
            except Exception as e:
                raise ValueError(f"Failed to parse response: {e}")

            if not response.is_normal():
                raise Exception(response.message)

            return response
        except Exception as e:
            Console.error(f"Error sending request: {e}")
            raise

    def on(self, path: str, callback: Callable[[IpcResponse], None]) -> None:
        """注册事件监听器"""
        if path not in self.listeners:
            self.listeners[path] = []
        self.listeners[path].append(callback)

    async def _handle_events(self) -> None:
        """处理服务器推送的事件"""
        try:
            while True:
                data = await self._recv_message()
                if not data:
                    break

                [req_dict, resp_dict] = msgpack.unpackb(data)
                request = IpcRequest(**req_dict)
                response = IpcResponse(**resp_dict)

                if request.path in self.listeners:
                    for callback in self.listeners[request.path]:
                        callback(response)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            Console.error(f"Error handling events: {e}")
        finally:
            self.writer.close()
            await self.writer.wait_closed()

    async def start(self) -> None:
        """启动事件循环"""
        await self._handle_events()

    async def close(self) -> None:
        """关闭连接"""
        self.writer.close()
        await self.writer.wait_closed()


class IpcSyncClient:
    def __init__(self, sock_path: str, timeout: float = 5.0):
        """初始化同步IPC客户端"""
        self.sock_path = sock_path
        self.client_id = str(uuid.uuid4())
        self.sock = None
        self.timeout = timeout
        self._connect()

    def _connect(self) -> None:
        """连接到IPC服务器"""
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect(self.sock_path)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to IPC server: {e}")

    def _send_message(self, data: bytes) -> None:
        """发送消息到服务器"""
        try:
            # 构造完整消息：8字节长度 + 数据内容
            message = len(data).to_bytes(8, byteorder='big') + data
            self.sock.sendall(message)
        except Exception as e:
            raise ConnectionError(f"Failed to send message: {e}")

    def _recv_message(self) -> bytes:
        """从服务器接收消息"""
        try:
            data = self.sock.recv(65536)
            if not data:
                raise ConnectionError("Connection closed by server")
            return data
        except socket.timeout:
            raise TimeoutError("Timeout while waiting for server response")
        except Exception as e:
            raise ConnectionError(f"Error receiving message: {e}")

    def send(self, path: str, data: Any = None) -> IpcResponse:
        """向指定路由发送数据并接收响应"""
        if not self.sock:
            raise ConnectionError("Not connected to server")

        try:
            # 创建并发送请求
            request = IpcRequest(
                id=str(uuid.uuid4()),
                clientId=self.client_id,
                path=path,
                header=IpcHeader(compress=False),
                body=data
            )
            self._send_message(msgpack.packb(
                request.to_dict(), use_bin_type=True))

            # 接收并解析响应
            response_data = self._recv_message()
            if not response_data:
                raise ConnectionError("Received empty response from server")

            try:
                [req_dict, resp_dict] = msgpack.unpackb(
                    response_data, raw=False)
                response = IpcResponse(**resp_dict)
            except Exception as e:
                raise ValueError(f"Failed to parse response: {e}")

            if not response.is_normal():
                raise Exception(response.message)

            return response

        except TimeoutError:
            Console.error("Request timed out")
            raise
        except ConnectionError as e:
            Console.error(f"Connection error: {e}")
            raise
        except Exception as e:
            Console.error(f"Error sending request: {e}")
            raise

    def close(self) -> None:
        """关闭连接"""
        if self.sock:
            self.sock.close()
            self.sock = None

    def __enter__(self):
        """支持with语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.close()
