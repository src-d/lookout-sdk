import os
import re
from setuptools import setup, find_packages

README = "../README.md"

description = "SDK for writing lookout analyzers"
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, README), encoding="utf-8") as f:
    long_description = "\n" + f.read()

# Get the version (borrowed from SQLAlchemy)
with open(os.path.join(here, "lookout", "sdk", "__init__.py")) as fp:
    VERSION = re.compile(r".*__version__ = \"(.*?)\"",
                         re.S).match(fp.read()).group(1)

setup(
    name="lookout-sdk",
    version=VERSION,
    description=description,
    license="Apache 2.0",
    author="source{d}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="applications@sourced.tech",
    url="https://github.com/meyskens/lookout-sdk",
    download_url="https://github.com/meyskens/lookout-sdk",
    packages=find_packages(),
    namespace_packages=["lookout"],
    keywords=["analyzer", "code-reivew"],
    install_requires=["grpcio>=1.13.0,<2.0",
                      "protobuf>=3.5.0,<4.0", "bblfsh>=2.12.7,<3.0"],
    package_data={"": ["../LICENSE.md", "../MAINTAINERS", README]},
    classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Topic :: Software Development :: Libraries"
    ],
)
