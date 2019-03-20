import unittest

from lookout.sdk.grpc import create_channel, create_server
from lookout.sdk import event_pb2
from lookout.sdk import pb
from lookout.sdk.test import mixins


class DummyAnalyzer(pb.AnalyzerServicer):

    def NotifyReviewEvent(self, request, context):
        return pb.EventResponse(comments=[pb.Comment(text='review')])

    def NotifyPushEvent(self, request, context):
        return pb.EventResponse(comments=[pb.Comment(text='push')])


class TestGRPCAnalyzerApi(mixins.TestWithRunningServicerMixin,
                          unittest.TestCase):

    def build_server(self):
        server = create_server(10)
        pb.add_analyzer_to_server(DummyAnalyzer(), server)

        return server

    def test_review(self):
        with create_channel(self._target) as channel:
            stub = pb.AnalyzerStub(channel)
            resp = stub.NotifyReviewEvent(event_pb2.ReviewEvent())

        self.assertEqual(len(resp.comments), 1)
        self.assertEqual(resp.comments[0].text, 'review')

    def test_push(self):
        with create_channel(self._target) as channel:
            stub = pb.AnalyzerStub(channel)
            resp = stub.NotifyPushEvent(event_pb2.PushEvent())

        self.assertEqual(len(resp.comments), 1)
        self.assertEqual(resp.comments[0].text, 'push')
