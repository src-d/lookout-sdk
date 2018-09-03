from setuptools import setup, find_packages

description = long_descr = "SDK for writing lookout analyzers"

VERSION = "0.0.1"

setup(
        name = "lookout_sdk",
        version = VERSION,
        description = description,
        license="Apache 2.0",
        author="source{d}",
        long_description=long_descr,
        author_email="applications@sourced.tech",
        url="https://github.com/src-d/lookout-sdk",
        download_url="https://github.com/src-d/lookout-sdk",
        packages=find_packages(),
        keywords=["analyzer", "code-reivew"],
        install_requires=["grpcio>=1.13.0", "protobuf>=3.6.0", "bblfsh"],
        package_data={"": ["../LICENSE", "../README.md", "MAINTAINERS"]},
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