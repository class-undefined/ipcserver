from typing import Optional


class Header:
    def __init__(self, path: str, id: str, compress: Optional[bool] = False):
        self.path = path
        self.id = id
        self.compress = compress  # 是否是压缩的数据 (暂未实现)

    def __str__(self) -> str:
        return f"Header(path={self.path}, id={self.id}, compress={self.compress})"
