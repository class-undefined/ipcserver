import asyncio
from ipcserver import IpcServer, IpcResponse, IpcRequest
app = IpcServer()


@app.route("/hello")
async def hello(request: "IpcRequest") -> "IpcResponse":
    return IpcResponse.ok(request.body)


if __name__ == "__main__":
    asyncio.run(app.run())
