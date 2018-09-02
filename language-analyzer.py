#!/usr/bin/env python3

# Example Analyser gRPC service implementation.
# Posts file-level comments for every file with language detected.

from concurrent.futures import ThreadPoolExecutor

import time
import grpc
# TODO(bzz): replace \w installed library path
from python import service_analyzer_pb2_grpc
from python import service_data_pb2_grpc
from python import service_data_pb2

from bblfsh import filter as filter_uast


port_to_listen = 2021
data_srv_addr = "localhost:10301"

class Analyzer(service_analyzer_pb2_grpc.AnalyzerServicer):
    def NotifyReviewEvent(self, request, context):
        print("got review request {}".format(request))

        # client connection to DataServe
        channel = grpc.insecure_channel(data_srv_addr)
        stub = service_data_pb2_grpc.DataStub(channel)
        changes = stub.GetChanges(
            service_data_pb2.ChangesRequest(
                head=request.head,
                base=request.base,
                want_contents=False,
                want_uast=True,
                exclude_vendored=True))
        for change in changes:
            print("analyzing '{}' in {}", change.head.path, change.head.language)
        #TODO filter_uast(uast, "")

    def NotifyPushEvent(self, request, context):
        pass

def serve():
    server = grpc.server(thread_pool=ThreadPoolExecutor(max_workers=10))
    service_analyzer_pb2_grpc.add_AnalyzerServicer_to_server(Analyzer(), server)
    server.add_insecure_port("0.0.0.0:{}".format(port_to_listen))
    server.start()

    # TODO(bzz)
    # - secure context
    # - max msg size

    one_day_sec = 60*60*24
    try:
        while True:
            time.sleep(one_day_sec)
    except KeyboardInterrupt:
        server.stop(0)

def main():
    print("starting gRPC Analyzer server at port {}".format(port_to_listen))
    serve()

if __name__ == "__main__":
    main()