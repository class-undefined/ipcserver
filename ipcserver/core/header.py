from typing import Optional


class IpcHeader:
    def __init__(self, compress: Optional[bool] = False):
        self.compress = compress  # 是否是压缩的数据 (暂未实现)

    def __str__(self) -> str:
        return f"IpcHeader(compress={self.compress})"

    def to_dict(self):
        return {"compress": self.compress}
