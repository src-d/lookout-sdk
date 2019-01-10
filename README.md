# lookout-sdk [![GitHub version](https://badge.fury.io/gh/src-d%2Flookout-sdk.svg)](https://github.com/src-d/lookout-sdk/releases) [![PyPI version](https://badge.fury.io/py/lookout-sdk.svg)](https://pypi.org/project/lookout-sdk/) [![Build Status](https://travis-ci.org/src-d/lookout-sdk.svg?branch=master)](https://travis-ci.org/src-d/lookout-sdk) [![GoDoc](https://godoc.org/gopkg.in/src-d/lookout-sdk.v0?status.svg)](https://godoc.org/gopkg.in/src-d/lookout-sdk.v0/pb)

Toolkit for writing new analyzers for **[source{d} Lookout](https://github.com/src-d/lookout)**.


# What Does the SDK Provide?

_For the complete documentation of **source{d} Lookout**, please take a look at [https://docs.sourced.tech/lookout](https://docs.sourced.tech/lookout)._

_For detailed information about the different parts of Lookout, and how they interact you can go to the [Lookout architecture guide](https://docs.sourced.tech/lookout/architecture)._

**lookout-sdk** provides:

- **proto [definitions](./proto)**.
- pre-generated libraries for [Golang](./pb) and [Python](./python), offering:
  - an easy **access to the DataService API though a gRPC service**. Lookout will take care of dealing with Git repositories, UAST extraction, programming language detection, etc.
  - low-level **helpers to work around some protobuf/gRPC caveats**.
- quickstart [examples](./examples) of an Analyzer that detects language and number of functions (written in Go and in Python).


# Caveats

For the gRPC client and server please follow these requirements:
- set a common maximum gRPC message size in gRPC servers and clients. This is required to avoid hitting different gRPC limits when handling UASTs, that can be huge &mdash;see [grpc/grpc#7927](https://github.com/grpc/grpc/issues/7927)&mdash;. To do so use the included helpers in lookout-sdk:
  - go: using `pb.NewServer` and `pb.DialContext`.
  - python: using `lookout.sdk.grpc.create_channel`.
- support [RFC 3986 URI scheme](https://github.com/grpc/grpc-go/issues/1911); lookout-sdk includes helpers for this:
  - go: using `pb.ToGoGrpcAddress` and `pb.Listen`.
  - python: using `lookout.sdk.grpc.to_grpc_address`.

## DataService

When DataService is being dialed, you should:

- disable secure connection:
  - python: using `server.add_insecure_port(address)` ([example](https://github.com/src-d/lookout-sdk/blob/master/examples/language-analyzer.py#L63)).
- turn off [gRPC fail-fast](https://github.com/grpc/grpc/blob/master/doc/wait-for-ready.md) mode if your analyzer creates a connection to DataServer before it was actually started. This way the RPCs are queued until the chanel is ready:
  - go: using `grpc.FailFast(false)`
([example](https://github.com/src-d/lookout-gometalint-analyzer/blob/7b4b37fb3109299516fbb43017934d131784f49f/cmd/gometalint-analyzer/main.go#L66)).


# Contributing

Contributions are **welcome and very much appreciated** 🙌

Please refer [to our Contribution Guide](docs/CONTRIBUTING.md) for more details.


## Community

source{d} has an amazing community of developers and contributors who are interested in Code As Data and/or Machine Learning on Code. Please join us! 👋

- [Slack](http://bit.ly/src-d-community)
- [Twitter](https://twitter.com/sourcedtech)
- [Email](mailto:hello@sourced.tech)


# Code of Conduct

All activities under source{d} projects are governed by the [source{d} code of conduct](.github/CODE_OF_CONDUCT.md).


# License

Apache License Version 2.0, see [LICENSE](LICENSE.md)
