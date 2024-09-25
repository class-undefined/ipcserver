from ..core.app import IpcServer
from ..core.request import IpcRequest
from ..core.header import IpcHeader
from typing import Dict, Optional
import uuid


class TestClient:
    __test__ = False

    def __init__(self, server: "IpcServer"):
        self.server = server.setup()

    async def send(self, path: str, data: Optional[Dict] = None):
        """
        # Example
        ```python
        from ipcserver import *

        app = IpcServer()
        def demo():
            v = APIRouter("/demo")

            @v.route("/")
            async def run(request: IpcRequest) -> IpcResponse:
                return IpcResponse.ok("ok")

            return v

        app.include_router(demo())

        @ipctest
        async def test01():
            client = TestClient(app)
            r = await client.send("/demo/")
            assert r.is_normal() == True
        ```
        """
        client_id = f"testclient-{id(self)}"
        req_id = str(uuid.uuid4())
        header = IpcHeader(compress=False)
        req = IpcRequest(id=req_id, path=path, header=header,
                         body=data, clientId=client_id)
        response = await self.server.handle_request(req)
        return response
