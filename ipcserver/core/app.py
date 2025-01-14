from typing import *
from .router import APIRouter
from ..utils import Console
from .config import IpcConfig
from .request import IpcRequest
from .response import IpcResponse, IpcStatus
from .header import IpcHeader
import asyncio
import traceback
import uuid
from asyncio import StreamReader, StreamWriter

if TYPE_CHECKING:
    from .router import Route

ExceptionHandler = Callable[["IpcRequest"], "IpcResponse"]


async def recv_msg(reader: StreamReader):
    # 读取8字节的消息长度
    raw_msglen = await reader.readexactly(8)
    if not raw_msglen:
        return None
    # 解析消息长度
    msglen = int.from_bytes(raw_msglen, byteorder='big')
    # 根据长度读取消息体
    data = await reader.readexactly(msglen)
    return data


class IpcServer:
    def __init__(self):
        self.config = IpcConfig.default()
        self.router = APIRouter()
        self.scopes: Dict[str, "Route"] = {}
        self.exception_handlers: Dict[type[Exception], ExceptionHandler] = {}
        self.clients: Dict[str, StreamWriter] = {}

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

    async def handle_request(self, request: "IpcRequest") -> "IpcResponse":
        route = self.match_route(request.path)
        if route:
            try:
                Console.log(request)
                return await route.func(request)
            except Exception as e:
                handler = self.exception_handlers.get(type(e))
                if handler:
                    return await handler(request)
                else:
                    Console.error(f"Invalid request: {traceback.format_exc()}")
                    return IpcResponse.error(message=str(e))
        else:
            Console.error("Route not found:", request.path)
            return IpcResponse.error("Route not found")

    async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
        addr = writer.get_extra_info('peername')
        Console.log("Python socket connected by", addr)
        req = None
        try:
            while True:
                data = await recv_msg(reader)
                if not data:
                    Console.warn("Python socket disconnected by", addr)
                    break
                try:
                    req = IpcRequest.from_data(data)
                except Exception as e:
                    Console.error(f"Invalid request: {traceback.format_exc()}")
                    try:
                        writer.write(IpcResponse.error(
                            data=None, message=str(e), code=IpcStatus.INTERNAL_SERVER_ERROR).to_bytes())
                        await writer.drain()
                    except (BrokenPipeError, ConnectionResetError):
                        Console.warn(
                            "Cannot send error response, client disconnected.")
                    continue
                if req.clientId not in self.clients:
                    self.clients[req.clientId] = writer
                try:
                    response = await self.handle_request(req)
                    writer.write(IpcResponse.make_bytes(req, response))
                    await writer.drain()
                except (BrokenPipeError, ConnectionResetError):
                    Console.warn("Cannot send response, client disconnected.")
                    break
        except asyncio.IncompleteReadError:
            Console.warn("Python socket disconnected by", addr)
        finally:
            if req.clientId in self.clients:
                self.clients.pop(req.clientId)
            writer.close()
            if writer.is_closing() is False:
                await writer.wait_closed()

    async def send(self, clientId: str, event: str, data: Any):
        writer = self.clients.get(clientId)
        if writer:
            header = IpcHeader(compress=False)
            req = IpcRequest(id=str(uuid.uuid4()), clientId=clientId,
                             path=event, header=header, body=data)
            response = IpcResponse.ok(data)
            writer.write(IpcResponse.make_bytes(req, response))
            await writer.drain()

    async def run(self, config: Optional["IpcConfig"] = None):
        self.config.update(config)
        self.setup()
        server = await asyncio.start_unix_server(
            self.handle_connection, path=self.config.sock)

        Console.log("Python socket is listening. Socket: ", self.config.sock)
        async with server:
            await server.serve_forever()
