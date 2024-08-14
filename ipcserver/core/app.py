from typing import *
from .router import APIRouter
from ..utils import Console
from .config import IpcConfig
from .request import IpcRequest
from .response import IpcResponse
import socket
import os
import traceback
if TYPE_CHECKING:
    from .router import Route

ExceptionHandler = Callable[["IpcRequest"], "IpcResponse"]


def recv_msg(conn: socket.socket):
    # 先读取4字节的消息长度
    raw_msglen = conn.recv(8)
    if not raw_msglen:
        return None
    # 解析消息长度
    msglen = int.from_bytes(raw_msglen, byteorder='big')
    # 然后根据长度读取消息体
    data = b''
    while len(data) < msglen:
        packet = conn.recv(msglen - len(data))
        if not packet:
            return None
        data += packet
    # 解码消息体
    return data


class IpcServer:
    def __init__(self):
        self.config = IpcConfig.default()
        self.router = APIRouter()
        self.scopes: Dict[str, "Route"] = {}
        self.exception_handlers: Dict[type[Exception], ExceptionHandler] = {}

    def route(self, path: str, name: Optional[str] = None, description: Optional[str] = None):
        """路由装饰器"""
        def decorator(func: Callable) -> Callable:
            self.router.add_route(path, func, name=name,
                                  description=description)
            return func
        return decorator

    def include_router(self, router: APIRouter, prefix: str = ''):
        self.router.include_router(router, prefix)

    def exception_handler(self, exception: Type[Exception]):
        """异常处理装饰器"""
        def decorator(func: ExceptionHandler) -> Callable:
            self.add_exception_handler(exception, func)
            return func
        return decorator

    def add_exception_handler(self, exception: Type[Exception], handler: ExceptionHandler):
        self.exception_handlers[exception] = handler

    def description(self):
        print("Registered routes:")
        for path, scope in self.scopes.items():
            Console.log(f"{scope}")

    def setup(self):
        """初始化路由"""
        for route in self.router.routes:
            self.scopes[route.path] = route
        self.description()
        return self

    def match_route(self, path: str):
        """路由匹配"""
        route = self.scopes.get(path)
        return route

    def __init_socket(self, sock: str):
        assert sock, "Socket path is required"
        if os.path.exists(sock):
            os.remove(sock)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(sock)
        server.listen(1)
        Console.log("Python socket is listening. Socket: ", sock)
        return server

    async def handle_request(self, request: "IpcRequest") -> "IpcResponse":
        route = self.match_route(request.header.path)
        Console.log(request)
        if route:
            try:
                return await route.func(request)
            except Exception as e:
                handler = self.exception_handlers.get(type(e))
                if handler:
                    return await handler(request)
                else:
                    return IpcResponse.error(str(e))
        else:
            Console.error("Route not found:", request.header.path)
            return IpcResponse.error("Route not found")

    async def run(self, config: Optional["IpcConfig"] = None):
        self.config.update(config)
        self.setup()
        server = self.__init_socket(self.config.sock)
        while True:
            conn, addr = server.accept()
            with conn:
                Console.log("Python socket connected by", addr)
                while True:
                    data = recv_msg(conn)
                    if not data:
                        Console.warn("Python socket disconnected by", addr)
                        break
                    try:
                        req = IpcRequest.from_data(data)
                    except Exception as e:
                        Console.error("Invalid request:",
                                      traceback.format_exc())
                    response = await self.handle_request(req)
                    conn.sendall(response.to_bytes())
