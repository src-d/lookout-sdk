import unittest
from unittest import mock

from lookout.sdk.grpc import \
    LogUnaryServerInterceptor, LogStreamServerInterceptor, \
    LogUnaryClientInterceptor, LogStreamClientInterceptor
from lookout.sdk.grpc.interceptors import base
from lookout.sdk.grpc import create_channel, create_server
from lookout.sdk.grpc.connection import grpc_max_msg_size
from tests.spy import spy_func


class TestChannelCreation(unittest.TestCase):

    target = "localhost:10301"

    def test_create_channel_default(self):
        with spy_func("grpc.insecure_channel") as m1:
            with spy_func("grpc.intercept_channel") as m2:
                create_channel(self.target)

                m1.assert_called_once_with(self.target, [
                    ("grpc.max_send_message_length", grpc_max_msg_size),
                    ("grpc.max_receive_message_length", grpc_max_msg_size),
                ])

                m2.assert_called_once_with(mock.ANY)

    def test_create_channel_with_options(self):
        with spy_func("grpc.insecure_channel") as m1:
            with spy_func("grpc.intercept_channel") as m2:
                create_channel(self.target, options=[
                    ("grpc.default_compression_level", 3)
                ])

                m1.assert_called_once_with(self.target, [
                    ("grpc.default_compression_level", 3),
                    ("grpc.max_send_message_length", grpc_max_msg_size),
                    ("grpc.max_receive_message_length", grpc_max_msg_size),
                ])

                m2.assert_called_once_with(mock.ANY)

    def test_create_channel_with_interceptors(self):
        i1 = LogUnaryClientInterceptor(lambda: None)
        i2 = LogStreamClientInterceptor(lambda: None)

        with spy_func("grpc.insecure_channel") as m1:
            with spy_func("grpc.intercept_channel") as m2:
                create_channel(self.target, interceptors=[i1, i2])

                m1.assert_called_once_with(self.target, [
                    ("grpc.max_send_message_length", grpc_max_msg_size),
                    ("grpc.max_receive_message_length", grpc_max_msg_size),
                ])

                m2.assert_called_once_with(mock.ANY, i1, i2)


class TestServerCreation(unittest.TestCase):

    def test_create_server_default(self):
        with spy_func("grpc.server") as m:
            create_server(1)

            m.assert_called_once()
            self.assertEqual(m.call_args[0][0]._max_workers, 1)
            m.assert_called_once_with(mock.ANY, options=[
                ("grpc.max_send_message_length", grpc_max_msg_size),
                ("grpc.max_receive_message_length", grpc_max_msg_size),
            ], interceptors=[])

    def test_create_server_with_options(self):
        with spy_func("grpc.server") as m:
            create_server(1, options=[("grpc.default_compression_level", 3)])

            m.assert_called_once()
            self.assertEqual(m.call_args[0][0]._max_workers, 1)
            m.assert_called_once_with(mock.ANY, options=[
                ("grpc.default_compression_level", 3),
                ("grpc.max_send_message_length", grpc_max_msg_size),
                ("grpc.max_receive_message_length", grpc_max_msg_size),
            ], interceptors=[])

    def test_create_server_with_interceptors(self):
        i1 = LogUnaryServerInterceptor(lambda: None)
        i2 = LogStreamServerInterceptor(lambda: None)

        with spy_func("grpc.server") as m:
            create_server(1, interceptors=[i1, i2])

            m.assert_called_once()
            self.assertEqual(m.call_args[0][0]._max_workers, 1)
            self.assertEqual(m.call_args[1]['options'], [
                ("grpc.max_send_message_length", grpc_max_msg_size),
                ("grpc.max_receive_message_length", grpc_max_msg_size),
            ])

            actual_interceptors = m.call_args[1]['interceptors']
            self.assertEqual(len(actual_interceptors), 2)

            for actual, expected_wrapped in zip(actual_interceptors, [i1, i2]):
                self.assertIsInstance(actual, base.ServerInterceptorWrapper)
                self.assertEqual(actual._wrapped, expected_wrapped)
