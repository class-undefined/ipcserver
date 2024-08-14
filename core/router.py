import asyncio
from typing import *
from ..utils import Console
if TYPE_CHECKING:
    from .request import IpcRequest
    from .response import IpcResponse
RouteFuncType = Callable[["IpcRequest"], "IpcResponse"]


class Route:
    def __init__(self, path: str, func: RouteFuncType, name: Optional[str] = None, description: Optional[str] = None):
        self.path = path
        self.func = func
        self.name = name
        self.description = description
        self.check_func()

    def is_async(self):
        """ 是否为异步函数 """
        return asyncio.iscoroutinefunction(self.func)

    def check_func(self):
        from .response import IpcResponse
        """ 检查函数是否为异步函数 以及返回值是否标记注解为 IpcResponse """
        assert self.is_async(
        ), f"Route function: {self.func.__name__} must be async"
        return_type = self.func.__annotations__.get("return")
        assert return_type is not None, f"Route function: {self.func.__name__} must have a return annotation"
        if isinstance(return_type, str):
            assert return_type == "IpcResponse", f"Route function: {self.func.__name__} must return IpcResponse"
        else:
            assert return_type == IpcResponse, f"Route function: {self.func.__name__} must return IpcResponse"

    def __str__(self):
        return f"Route(path={self.path})"


class APIRouter:
    def __init__(self, prefix=""):
        if prefix:
            assert prefix.startswith("/"), "A path prefix must start with '/'"
            assert not prefix.endswith(
                "/"
            ), "A path prefix must not end with '/', as the routes will start with '/'"
        self.prefix = prefix
        self.routes: List[Route] = []

    def add_route(self, path: str, func: RouteFuncType, name: Optional[str] = None, description: Optional[str] = None):
        route = Route(self.prefix + path, func,
                      name=name, description=description)
        self.routes.append(route)

    def include_api_router(self, api_router: "APIRouter"):
        """ 导入APIRouter """
        for route in api_router.routes:
            path = f"{self.prefix}{route.path}"
            route = Route(path,
                          route.func,
                          name=route.name,
                          description=route.description)
            self.routes.append(route)

    def include_router(self, api_router: "APIRouter", prefix: str = ""):
        """ 导入APIRouter (在`include_api_router`基础上额外增加一个 `prefix`) """
        for route in api_router.routes:
            path = f"{self.prefix}{prefix}{route.path}"
            route = Route(path,
                          route.func,
                          name=route.name,
                          description=route.description)
            self.routes.append(route)

    def route(self, path: str, name: Optional[str] = None, description: Optional[str] = None):
        """ ipc 路由注解 """
        def decorator(func: RouteFuncType):
            self.add_route(path, func, name=name, description=description)
            return func
        return decorator
