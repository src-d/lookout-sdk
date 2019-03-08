#!/usr/bin/env python3

"""
 Example Analyzer gRPC service implementation.
 Posts file-level comments for every file with language detected.
"""

import time
from lookout.sdk import pb
from lookout.sdk.grpc import to_grpc_address, create_channel, create_server

from bblfsh import filter as filter_uast


port_to_listen = 9930
data_srv_addr = to_grpc_address("ipv4://localhost:10301")
version = "alpha"


class Analyzer(pb.AnalyzerServicer):

    @pb.wrap_context
    def NotifyReviewEvent(self, request, context):
        print("got review request {}".format(request))

        comments = []

        # client connection to DataServe
        with create_channel(data_srv_addr) as channel:
            stub = pb.DataStub(channel)

            # Add some log fields that will be available to the data server
            # using `context.add_log_fields`.
            context.add_log_fields({
                "some-string-key": "some-value",
                "some-int-key":    1,
            })

            changes = stub.get_changes(
                context,
                pb.ChangesRequest(
                    head=request.commit_revision.head,
                    base=request.commit_revision.base,
                    want_contents=False,
                    want_uast=True,
                    exclude_vendored=True))

            for change in changes:
                if not change.HasField("head"):
                    continue

                print("analyzing '{}' in {}".format(
                    change.head.path, change.head.language))
                fns = list(filter_uast(change.head.uast, "//*[@roleFunction]"))
                text = "language: {}, functions: {}".format(
                    change.head.language, len(fns))
                comments.append(pb.Comment(
                    file=change.head.path, line=0, text=text))

        return pb.EventResponse(analyzer_version=version, comments=comments)

    @pb.wrap_context
    def NotifyPushEvent(self, request, context):
        pass


def serve():
    server = create_server(10)
    pb.add_analyzer_to_server(Analyzer(), server)
    server.add_insecure_port("0.0.0.0:{}".format(port_to_listen))
    server.start()

    one_day_sec = 60 * 60 * 24
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
