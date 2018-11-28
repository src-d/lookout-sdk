import io
import os
from setuptools import setup, find_packages

VERSION = "0.2.0"
README = '../README.md'

description = "SDK for writing lookout analyzers"
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, README), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
        name="lookout_sdk",
        version=VERSION,
        description=description,
        license="Apache 2.0",
        author="source{d}",
        long_description=long_description,
        long_description_content_type='text/markdown',
        author_email="applications@sourced.tech",
        url="https://github.com/src-d/lookout-sdk",
        download_url="https://github.com/src-d/lookout-sdk",
        packages=find_packages(),
        keywords=["analyzer", "code-reivew"],
        install_requires=["grpcio==1.13.0", "protobuf==3.6.1", "bblfsh"],
        package_data={"": ["../LICENSE", "../MAINTAINERS", README]},
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
