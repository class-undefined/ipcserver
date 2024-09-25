import asyncio
from ipcserver import IpcServer, IpcResponse, IpcRequest, APIRouter, TestClient, ipctest

app = IpcServer()


def demo():
    v = APIRouter("/demo")

    @v.route("/")
    async def run(request: IpcRequest) -> IpcResponse:
        return IpcResponse.ok("ok")

    @v.route("/hello")
    async def stop(request: IpcRequest) -> IpcResponse:
        return IpcResponse.ok("hello")
    return v


app.include_router(demo())


@ipctest
async def test01():
    client = TestClient(app)
    r = await client.send("/demo/")
    assert r.is_normal() == True


if __name__ == "__main__":
    asyncio.run(app.run())
