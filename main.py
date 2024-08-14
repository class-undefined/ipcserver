from .core.app import IpcServer
import asyncio


if __name__ == "__main__":
    asyncio.run(IpcServer().run())
