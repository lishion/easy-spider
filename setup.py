import setuptools
from os.path import join

with open("readme.md", encoding='utf-8') as fd:
    long_description = fd.read()

with open("requirements.txt", encoding="utf-8") as fd:
    install_requires = [line for line in fd.read().split("\n") if line]

with open(join("easy_spider", "__init__.py")) as fd:
    for line in fd:
        line = line.lstrip(" ")
        if line.startswith("__version__"):
            try:
                version = line.split("=")[1].strip().strip('"')
            except Exception as e:
                raise Exception("find version error, cause by `{}`".format(e))

packages = setuptools.find_packages(exclude=("test", "demo"))

setuptools.setup(
    name="easy-spider",
    version=version,
    author="lin3x",
    author_email="544670411@qq.com",
    description="A asynchronous spider with aiohttp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://lin3x.coding.net/p/easy_spider",
    packages=packages,
    data_files=('readme.md', 'requirements.txt'),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
