from ..router import APIRouter
from ..response import IpcResponse


def test01():
    router = APIRouter("/api")
    group_router = APIRouter("/group")

    @group_router.route("/test")
    async def test() -> "IpcResponse":
        return IpcResponse.ok("test")

    router.include_api_router(group_router)
    assert len(router.routes) == 1
    assert router.routes[0].path == "/api/group/test"
