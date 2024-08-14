from setuptools import setup, find_packages
setup(
    name="ipcserver",
    version="0.1.2",
    packages=find_packages(exclude=['tests', 'tests.*']),
    description="A fastapi-like but a sock server",
    install_requires=[
        "colorama>=0.4.6",
        "msgpack>=1.0.8"
    ],
    author="class-undefined",
    author_email="luyukai@tsinghua.edu.cn",
    python_requires='>=3.6',
)
