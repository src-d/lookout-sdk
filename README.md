lookout SDK [![GoDoc](https://godoc.org/gopkg.in/src-d/lookout-sdk.v0?status.svg)](https://godoc.org/github.com/src-d/lookout-sdk) [![PyPI version](https://badge.fury.io/py/lookout-sdk.svg)](https://pypi.org/project/lookout-sdk/) [![Build Status](https://travis-ci.org/src-d/src-d/lookout-sdk.svg)](https://travis-ci.org/src-d/src-d/lookout-sdk)
-----------

What is lookout SDK?
===================
Lookout SDK is toolkit for writing new analyzers for the [lookout](https://github.com/src-d/lookout/).


What does it provide
====================
It provides to analyzer an easy access to the DataService API though gRPC service.

DataService abstracts all data access and details of dealing witn actual Git repositories, UAST extraction, programming language detection, etc. This way analyzer can only focus on source code analysis logic.

Architecture of lookout and it's componetes are described in [src-d/lookout/docs](https://github.com/src-d/lookout/tree/master/docs#lookout)

SDK includes:
 - proto definitinos
 - pre-generate libraries code for Golang and Python
 - quickstart documentation on how to write an anlyzer


How to create a new Analyzer
============================

Essentially, every analyzer is a [gRCP server](https://grpc.io/docs/guides/#overview) that implements [Analyzer service](TK link). Lookout itself act as a gRCP client and will push your analyzer whenever there is a new PR is ready for anlysis.

### Golang
 - using pre-generated code `gopkg.in/src-d/lookout-sdk.v0/pb`
 - implement Analyzer service interface. Example:
```go
NotifyReviewEvent(ctx context.Context, review *pb.ReviewEvent) (*pb.EventResponse, error)
NotifyPushEvent(context.Context, *pb.PushEvent) (*pb.EventResponse, error)
```
   - analyzer should request [a stream of](https://grpc.io/docs/tutorials/basic/go.html#server-side-streaming-rpc-1) files and UASTs from [DataService](TK link) (that lookout provides, by default on `localhost:10301`)
   - analyzer have options to ask for UAST, language, full file content or exclude paths: by regexp, or just all [vendored paths](TK link to enry or linguist)
   - analyzer just need to return a list of [Comment](TK link to .proto definitions) messages
 - run gRPC server to listen for requests from the lookout

 SDK contains a quickstart exmaple of Analyzer that detects language for every file `language-analyzer.go`.

 (For your conveniece, there is also a bootstrapped application project with SDK, CI, vendoring using godep, etc at [src-d/lookout-example-analyzer-go]())


### Python

 - `pip install lookout-sdk`
 - using pre-generated code (TK python import)
 - register and listen


TODOs:
.proto
README
 - links to pypi, godoc, travis
.sh
.travis.yml
 - make no-changes-in-commit
 - publish on pypi
 -

How to test analyzer
====================
 - get `lookout-sdk` binary
 - run `bblfshd`
 - start analyzer e.g.
   - `go get -u .`
   - `go run language-analyzer.go` ,
   or
   - `pip3 install lookout-sdk`
   - `python3 language-analyzer.py`
 - test \wo Github access, on the latest commit in the local Git repository
```
/lookout review \
  --log-level=debug \
  --git-dir="$GOPATH/src/gopkg.in/src-d/lookout-sdk.v0" \
  "ipv4://localhost:2020"
```

 this will generate a mock Review event and notify the analyzer.

(TK lookout-sdk binary desctiption + options)


After

Cavets
======
 - client: disable secure connection on dialing with `grpc.WithInsecure()`
 - client: turn off gRCP [fail-fast](TK link)
 - client/server: set max gRCP message size


How to update SDK
=================
 - re-generate all the code using (TK link to .sh), commit
 - tag a realease


 # License

[Apache License v2.0](./LICENSE)
