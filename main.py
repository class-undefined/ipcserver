import asyncio
from ipcserver import IpcServer, IpcResponse, IpcRequest, APIRouter

app = IpcServer()


def virtuoso():
    v = APIRouter("/virtuoso")

    @v.route("/run")
    async def run(request: IpcRequest) -> IpcResponse:
        return IpcResponse.ok("run")

    @v.route("/stop")
    async def stop(request: IpcRequest) -> IpcResponse:
        return IpcResponse.ok("stop")

    @v.route("/clients")
    async def stop(request: IpcRequest) -> IpcResponse:
        print(app.clients)
        await app.send(request.clientId, "/msg", 123)
        return IpcResponse.ok("stop")

    return v


app.include_router(virtuoso())


if __name__ == "__main__":
    asyncio.run(app.run())
