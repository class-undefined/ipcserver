from ipcserver.core.client import IpcSyncClient


def test01():
    sock_path = "/tmp/ipcserver.sock"
    client = IpcSyncClient(sock_path)
    res = client.send("/demo/", data={"a": 1})
    print(res)
