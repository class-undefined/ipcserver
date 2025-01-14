from ipcserver.core.client import SyncIpcClient


def test01():
    sock_path = "/tmp/ipcserver.sock"
    client = SyncIpcClient(sock_path)
    res = client.send("/demo/", data={"a": 1})
    print(res)
