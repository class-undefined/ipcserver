import asyncio
from ipcserver import IpcServer, IpcResponse, IpcRequest
app = IpcServer()


@app.route("/hello")
async def hello(request: "IpcRequest") -> "IpcResponse":
    print(request.header)
    return IpcResponse.ok("Hello, World!")


if __name__ == "__main__":
    asyncio.run(app.run())
