from typing import Optional


class Header:
    def __init__(self, path: str, compress: Optional[bool] = False):
        self.path = path
        self.compress = compress  # 是否是压缩的数据
