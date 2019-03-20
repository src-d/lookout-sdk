import socket
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing

import unittest

import grpc

from lookout.sdk import pb
from lookout.sdk.service_data import DataStub
from lookout.sdk.grpc import create_channel, create_server, \
    LogUnaryServerInterceptor, \
    LogStreamServerInterceptor, \
    LogUnaryClientInterceptor, \
    LogStreamClientInterceptor
from lookout.sdk import event_pb2


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class DummyAnalyzer(pb.AnalyzerServicer):

    def notify_review_event(self, request, context):
        return pb.EventResponse()

    def notify_push_event(self, request, context):
        return pb.EventResponse()


class DummyDataServicer(pb.DataServicer):

    def GetChanges(self, request, context):
        return pb.Change()

    def GetFiles(self, request, context):
        return pb.File()


class LogFnTracker:

    def __init__(self):
        self.counter = {"unary": 0, "stream": 0}
        self.logs = []

    def unary(self, log_fields, msg):
        self._record(log_fields, msg, "unary")

    def stream(self, log_fields, msg):
        self._record(log_fields, msg, "stream")

    def _record(self, log_fields, msg, key):
        self.counter[key] += 1
        self.logs.append((log_fields.fields.copy(), msg))


class TestWithRunningServicerMixin:

    def setUp(self):
        self._tracker = LogFnTracker()
        self._target = "0.0.0.0:{}".format(find_free_port())
        self._server = self.build_server()
        self._server.add_insecure_port(self._target)
        self._server.start()

    def tearDown(self):
        self._server.stop(0)


class TestServerLoggerInterceptors(TestWithRunningServicerMixin,
                                   unittest.TestCase):

    def build_server(self):
        server = create_server(10, interceptors=[
            LogUnaryServerInterceptor(self._tracker.unary),
            LogStreamServerInterceptor(self._tracker.stream),
        ])
        pb.add_analyzer_to_server(DummyAnalyzer(), server)

        return server

    def test_interceptors_called(self):
        with create_channel(self._target) as channel:
            stub = pb.AnalyzerStub(channel)
            stub.NotifyReviewEvent(event_pb2.ReviewEvent())

        self.assertEqual(self._tracker.counter, {"unary": 2, "stream": 0})

        first_unary = self._tracker.logs[0]
        first_log_fields = first_unary[0]
        self.assertEqual(first_log_fields, {
            "system": "grpc",
            "span.kind": "server",
            "grpc.service": "pb.Analyzer",
            "grpc.method": "NotifyReviewEvent",
        })
        self.assertEqual(first_unary[1], "gRPC unary server call started")

        second_unary = self._tracker.logs[1]
        second_log_fields = second_unary[0]
        self.assertEqual(set(second_log_fields.keys()),
                         {"system", "span.kind", "grpc.service", "grpc.method",
                          "grpc.code", "grpc.start_time", "duration"})

        second_log_fields.pop("grpc.start_time")
        second_log_fields.pop("duration")
        self.assertEqual(second_log_fields, {
            "system": "grpc",
            "span.kind": "server",
            "grpc.service": "pb.Analyzer",
            "grpc.method": "NotifyReviewEvent",
            "grpc.code": "OK"
        })
        self.assertEqual(second_unary[1], "gRPC unary server call finished")


class TestClientLoggerInterceptors(TestWithRunningServicerMixin,
                                   unittest.TestCase):

    def build_server(self):
        server = grpc.server(ThreadPoolExecutor(max_workers=10))
        pb.add_dataservicer_to_server(DummyDataServicer(), server)

        return server

    def test_interceptors_called(self):
        with create_channel(self._target, interceptors=[
                LogUnaryClientInterceptor(self._tracker.unary),
                LogStreamClientInterceptor(self._tracker.stream),
        ]) as channel:
            stub = DataStub(channel)
            stub.get_changes(None, pb.ChangesRequest())

        self.assertEqual(self._tracker.counter, {"unary": 0, "stream": 2})

        first_streaming = self._tracker.logs[0]
        first_log_fields = first_streaming[0]
        self.assertEqual(first_log_fields, {
            "system": "grpc",
            "span.kind": "client",
            "grpc.service": "pb.Data",
            "grpc.method": "GetChanges",
        })
        self.assertEqual(first_streaming[1],
                         "gRPC streaming client call started")

        second_streaming = self._tracker.logs[1]
        second_log_fields = second_streaming[0]
        self.assertEqual(set(second_log_fields.keys()),
                         {"system", "span.kind", "grpc.service", "grpc.method",
                          "grpc.code", "grpc.start_time", "duration"})

        second_log_fields.pop("grpc.start_time")
        second_log_fields.pop("duration")
        self.assertEqual(second_log_fields, {
            "system": "grpc",
            "span.kind": "client",
            "grpc.service": "pb.Data",
            "grpc.method": "GetChanges",
            "grpc.code": "OK"
        })
        self.assertEqual(second_streaming[1],
                         "gRPC streaming client call finished")
