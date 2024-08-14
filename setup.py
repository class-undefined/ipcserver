from setuptools import setup, find_packages
setup(
    name="ipcserver",
    version="0.1.0",
    packages=find_packages(include=["."], exclude=['tests', 'tests.*']),
    description="A fastapi-like but a sock server",
    install_requires=[
        line.strip() for line in open('requirements.txt')
    ],
    author="class-undefined",
    author_email="luyukai@tsinghua.edu.cn",
    python_requires='>=3.6',
)
