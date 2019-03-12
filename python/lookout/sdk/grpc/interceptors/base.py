from typing import Union

import grpc

ServerInterceptor = Union[
    'UnaryServerInterceptor',
    'StreamServerInterceptork'
]


class ServerInterceptorWrapper(grpc.ServerInterceptor):
    """gRPC server interceptor wrapper

    Unfortunately at time of writing (`grpcio==1.18.0`) gRPC doesn't provide
    an api to create a server interceptor for each type of invocation:
        - unary-unary,
        - unary-stream,
        - stream-unary,
        - stream-stream.

    But it provides a single interface for all methods:
        https://github.com/grpc/grpc/blob/f6cba4b2fba2fd529d68146a4725b56e806cc6f2/src/python/grpcio/grpc/__init__.py#L1275

    This class is a sort of hack that permits the user to have a clean api to
    create server interceptors for each gRPC method type. Currently the
    following classes are provided (similarly to the Go SDK):
        - `lookout.sdk.grpc.interceptors.base.UnaryServerInterceptor`,
        - `lookout.sdk.grpc.interceptors.base.ServerServerInterceptor`.

    The first one intercepts both unary-unary and stream-unary invocations (so
    the invocations where the server response is unary).
    The second one intercepts both unary-stream and stream-stream invocations
    (so the invocations where the server response is a stream).

    More fine-grainded distinction could be easily added.

    This wrapper only needs the server it is attached to. Everytime a request
    is intercepted through the `intercept_service` method exposed by the
    `grpc.ServerInterceptor` interface, the type of the RPC method handler
    is checked against the type of wrapped interceptor. If the types match,
    then the interceptor is called, otherwise it is skipped.

    """
    def __init__(self, wrapped: ServerInterceptor):
        """Wraps the provided server interceptor"""
        self._wrapped = wrapped
        self._server = None

    def bind(self, server: grpc.Server):
        """Binds the provided server"""
        self._server = server

    def intercept_service(self, continuation, handler_call_details):
        """Intercepts incoming RPCs before handing them over to a handler

        See `grpc.ServerInterceptor.intercept_service`.

        """
        method = handler_call_details.method
        rpc_method_handler = self._server._state.generic_handlers[0]\
                                                ._method_handlers[method]
        if rpc_method_handler.response_streaming:
            if self._wrapped.is_streaming:
                # `self._wrapped` is a `StreamServerInterceptor`
                return self._wrapped.intercept_service(
                    continuation, handler_call_details)
        else:
            if not self._wrapped.is_streaming:
                # `self._wrapped` is a `UnaryServerInterceptor`
                return self._wrapped.intercept_service(
                    continuation, handler_call_details)

        # skip the interceptor due to type mismatch
        return continuation(handler_call_details)


class UnaryClientInterceptor(grpc.UnaryUnaryClientInterceptor,
                             grpc.StreamUnaryClientInterceptor):
    """Client interceptor for invocations whose response is unary"""

    def intercept_unary_unary(self, continuation, client_call_details,
                              request):
        return self.intercept_unary(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details,
                               request):
        return self.intercept_unary(continuation, client_call_details, request)

    def intercept_unary(self, continuation, client_call_details, request):
        raise NotImplementedError()


class StreamClientInterceptor(grpc.UnaryStreamClientInterceptor,
                              grpc.StreamStreamClientInterceptor):
    """Client interceptor for invocations whose response is a stream"""

    def intercept_unary_stream(self, continuation, client_call_details,
                               request_iterator):
        return self.intercept_stream(continuation, client_call_details,
                                     request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details,
                                request_iterator):
        return self.intercept_stream(continuation, client_call_details,
                                     request_iterator)

    def intercept_stream(self, continuation, client_call_details, request):
        raise NotImplementedError()


class UnaryServerInterceptor(grpc.ServerInterceptor):
    """Server interceptor for requests whose response is unary"""

    @property
    def is_streaming(self):
        return False

    def intercept_service(self, continuation, handler_call_details):
        raise NotImplementedError()


class StreamServerInterceptor(grpc.ServerInterceptor):
    """Server interceptor for requests whose response is a stream"""

    @property
    def is_streaming(self):
        return True

    def intercept_service(self, continuation, handler_call_details):
        raise NotImplementedError()
