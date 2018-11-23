lookout SDK [![GoDoc](https://godoc.org/gopkg.in/src-d/lookout-sdk.v0?status.svg)](https://godoc.org/github.com/src-d/lookout-sdk) [![PyPI version](https://badge.fury.io/py/lookout-sdk.svg)](https://pypi.org/project/lookout-sdk/) [![Build Status](https://travis-ci.org/src-d/lookout-sdk.svg)](https://travis-ci.org/src-d/lookout-sdk)
-----------

What is lookout SDK?
===================
Lookout SDK is a toolkit for writing new analyzers for the [lookout](https://github.com/src-d/lookout/).


What does it provide
====================
It provides to an analyzer an easy access to the DataService API though a gRPC service.

DataService abstracts all data access and details of dealing with actual Git repositories, UAST extraction, programming language detection, etc. This way the analyzer can focus focus only on source code analysis logic.

The architecture of lookout and its components are described in [src-d/lookout/docs](https://github.com/src-d/lookout/tree/master/docs#lookout)

**SDK includes:**
 - proto [definitions](./proto)
 - pre-generated libraries code for [Golang](./pb) and [Python](./python)
 - low-level helpers to workaround protobuf/gRPC caveats. Check [go documentation](https://godoc.org/gopkg.in/src-d/lookout-sdk.v0/pb)
 - quickstart documentation on [how to write an analyzer](#how-to-create-a-new-analyzer)


How to create a new Analyzer
============================

Essentially, every analyzer is just a [gRPC server](https://grpc.io/docs/guides/#overview) that implements [Analyzer service](./proto/lookout/sdk/service_analyzer.proto#L30). Lookout itself acts as a gRPC client for this server and it will push the analyzer server whenever a new  Pull Request is ready for analysis.

### Golang
Steps:
 - use pre-generated code for gRPC from `gopkg.in/src-d/lookout-sdk.v0/pb`
 - implement Analyzer service interface. Example:
   ```go
   NotifyReviewEvent(ctx context.Context, review *pb.ReviewEvent) (*pb.EventResponse, error)
   NotifyPushEvent(context.Context, *pb.PushEvent) (*pb.EventResponse, error)
   ```
   - analyzer should request [a stream of](https://grpc.io/docs/tutorials/basic/go.html#server-side-streaming-rpc-1) files and UASTs from [DataService](./proto/lookout/sdk/service_data.proto#L27) that lookout exposes, by default, on `localhost:10301`
   - analyzer has [options](./proto/lookout/sdk/service_data.proto#L61) to ask either for all files, or just the changed ones, as well as UASTs, language, full file content and/or exclude some paths: by regexp, or just all [vendored paths](https://github.com/github/linguist/blob/master/lib/linguist/vendor.yml)
   - analyzer has to return a list of [Comment](./proto/lookout/sdk/service_analyzer.proto#L42) messages
 - run gRPC server to listen for requests from the lookout

 SDK contains a quickstart example of an Analyzer that detects language and number of functions for every file [language-analyzer.go](./language-analyzer.go):
  - `go get -u .`
  - `go run language-analyzer.go`


### Python

 - `pip install lookout-sdk`
 - use pre-generated code for gRPC from [`lookout_sdk`](https://pypi.org/project/lookout-sdk/) library
 - implement Analyzer class that extends [AnalyzerServicer](./python/lookout/sdk/service_analyzer_pb2_grpc.py#34). Example:
   ```python
   def NotifyReviewEvent(self, request, context):
   def NotifyPushEvent(self, request, context):
   ```
   - analyzer should request [a stream of](https://grpc.io/docs/tutorials/basic/python.html#response-streaming-rpc) files and UASTs from [DataService](./proto/lookout/sdk/service_data.proto#L27) that lookout exposes, by default, on `localhost:10301`
   - analyzer has [options](./proto/lookout/sdk/service_data.proto#L61) to ask either for all files, or just the changed ones, as well as UASTs, language, full file content and/or exclude some paths: by regexp, or just all [vendored paths](https://github.com/github/linguist/blob/master/lib/linguist/vendor.yml)
   - analyzer has to return a list of [Comment](./proto/lookout/sdk/service_analyzer.proto#L42) messages
 - start [grpc server](https://grpc.io/docs/tutorials/basic/python.html#starting-the-server) and add Analyzer instance to it

SDK contains a quickstart example of an Analyzer that detects language and number of functions for every file [language-analyzer.py](./language-analyzer.py):
 - `python3 language-analyzer.py`


How to test analyzer
====================
One can test analyzer locally without the need for Github access and a full lookout server installation using `lookout-sdk` binary. You can think about it as curl-like tool to call an analyzer gRPC endponts. For convenience, it also exposes a DataServer backed by a git repository in local FS.

 - get `lookout-sdk` binary from [src-d/lookout releases](https://github.com/src-d/lookout/releases)
 - run [`bblfshd`](https://doc.bblf.sh/using-babelfish/getting-started.html)
 - build and start analyzer e.g. Golang
   - `go get -u .`
   - `go run language-analyzer.go` ,
   or Python
   - `pip install lookout-sdk`
   - `python3 language-analyzer.py`
 - test **without** Github access, on the latest commit in some Git repository in local FS
   ```
   $ lookout-sdk review \
     --log-level=debug \
     --git-dir="$GOPATH/src/gopkg.in/src-d/lookout-sdk.v0" \
     "ipv4://localhost:2020"
   ```

this will create a "mock" Review event and notify the analyzer, as if you were creating a Pull Request from `HEAD~1`.

Check [src-d/lookout](https://github.com/src-d/lookout/tree/master/sdk#lookout-sdk-commands) for further details on `lookout-sdk` binary CLI options.


Extracting UAST from arbitrary code
===================================

Lookout server and `lookout-sdk` binary proxy bblfsh gRPC protocol through DataServer.

Please check how to create client in [bblfsh documentation](https://docs.sourced.tech/babelfish) and use DataServer address to connect.


Caveats
========
 - client: disable secure connection on dialing with `grpc.WithInsecure()`
 - client/server: set [max gRPC message size](https://github.com/grpc/grpc/issues/7927):
    - go: use `pb.NewServer` and `pb.DialContext` instead.
 - client: turn off [gRPC fail-fast](https://github.com/grpc/grpc/blob/master/doc/wait-for-ready.md) mode
   If your analyzer greedy creates a connection to DataServer before one was actually started, you might want to disable fail-fast mode. This way the RPCs are queued until the chanel ready. Here is an [example](https://github.com/src-d/lookout-gometalint-analyzer/blob/7b4b37fb3109299516fbb43017934d131784f49f/cmd/gometalint-analyzer/main.go#L66).
  - go client/server: use `pb.ToGoGrpcAddress` and `pb.Listen` to support [RFC 3986 URI scheme](https://github.com/grpc/grpc-go/issues/1911)

Release Process
=================
 - Make sure the code is up to date using `make protogen`.
 - Update `VERSION` in `python/setup.py` with the same version that you will use for the tag (manual step required until [#2](https://github.com/src-d/lookout-sdk/issues/2) is implemented).
 - Create the release tag.

 # License
[Apache License v2.0](./LICENSE)
