# ipcserver

A fastapi-like but a sock server

## Installation

```bash
git clone https://github.com/class-undefined/ipcserver.git
cd ipcserver
pip install .
```

## Usage

```python
from ipcserver import IPCServer, IPCResponse
import asyncio


app = IPCServer()
@app.route('/hello')
async def hello() -> "IPCResponse": # `async`, return IPCResponse and typing is required
    return IPCResponse.ok('Hello World')

if __name__ == '__main__':
    asyncio.run(app.run())
```
