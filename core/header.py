class Header:
    def __init__(self, path: str, compress: bool):
        self.path = path
        self.compress = compress  # 是否是压缩的数据
