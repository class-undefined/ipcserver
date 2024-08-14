# ipcserver

A fastapi-like but a sock server

## Installation

```bash
pip install ipcserver
```

## Usage

```python
from ipcserver import IPCServer, IPCResponse, IpcRequest
import asyncio


app = IPCServer()


@app.route('/hello')
async def hello(request: "IpcRequest") -> "IPCResponse": # `async`, return IPCResponse and typing is required
    return IPCResponse.ok('Hello World')

if __name__ == '__main__':
    asyncio.run(app.run())
```
