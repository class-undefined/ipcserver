import asyncio
from ipcserver import IpcServer, IpcResponse
app = IpcServer()


@app.route("/hello")
async def hello() -> "IpcResponse":
    return IpcResponse.ok("Hello, World!")


if __name__ == "__main__":
    asyncio.run(app.run())
