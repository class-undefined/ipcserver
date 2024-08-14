import struct
from ..request import IpcRequest


def test01():
    def create_message(path, header, body):
        path_bytes = path.encode('utf-8')
        header_bytes = header.encode('utf-8')
        body_bytes = body.encode('utf-8')

        # 计算每段的长度
        path_length = len(path_bytes)
        header_length = len(header_bytes)
        body_length = len(body_bytes)

        # 使用 struct.pack 将长度转为 4 字节的整数
        message = struct.pack('!Q', path_length) + path_bytes
        message += struct.pack('!Q', header_length) + header_bytes
        message += struct.pack('!Q', body_length) + body_bytes

        return message

    message = create_message("path", "header", "body")
    path, header, body = IpcRequest.from_data(message)
    print(path, header, body)
