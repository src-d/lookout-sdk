import functools
from datetime import datetime
from typing import Callable, Union

import grpc

from lookout.sdk.grpc.log_fields import LogFields
from lookout.sdk.grpc.interceptors import base


class LogInterceptorMixin:
    """Provides methods to add log fields for request/response for logging"""

    # Can be either 'server' or 'client' depending on the interceptor type
    KIND = None

    def __init__(self, log_fn: Callable[[LogFields, str], None]):
        """Initializes the logger interceptor with the given log function"""
        self._log_fn = log_fn

    def add_request_log_fields(
            self, log_fields: LogFields,
            call_details: Union[grpc.HandlerCallDetails,
                                grpc.ClientCallDetails]
    ):
        """Add log fields related to a request to the provided log fields

        :param log_fields: log fields instance to which to add the fields
        :param call_details: some information regarding the call

        """
        service, method = call_details.method[1:].split("/")
        log_fields.add_fields({
            "system":       "grpc",
            "span.kind":    self.KIND,
            "grpc.service": service,
            "grpc.method":  method,
        })

    def add_response_log_fields(self, log_fields: LogFields,
                                start_time: datetime, err: Exception):
        """Add log fields related to a response to the provided log fields

        :param log_fields: log fields instnace to which to add the fields
        :param start_time: start time of the request
        :param err: exception raised during the handling of the request.

        """
        code = "Unknown" if err is not None else "OK"
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        log_fields.add_fields({
            "grpc.start_time": start_time.isoformat() + "Z",
            "grpc.code":       code,
            "duration":        "{duration}ms".format(duration=duration),
        })


class LogClientInterceptorMixin(LogInterceptorMixin):
    """Logger interceptor for client"""

    KIND = "client"
    PRE_REQUEST_MESSAGE = "gRPC client call started"
    POST_REQUEST_MESSAGE = "gRPC client call finished"

    def intercept(self, continuation, client_call_details, request):
        log_fields = LogFields.from_metadata(
            dict(client_call_details.metadata or {}))

        self.add_request_log_fields(
            log_fields, client_call_details)

        self._log_fn(log_fields, self.PRE_REQUEST_MESSAGE)

        start = datetime.utcnow()
        out = continuation(client_call_details, request)
        self.add_response_log_fields(log_fields, start, None)

        self._log_fn(log_fields, self.POST_REQUEST_MESSAGE)

        return out


class LogUnaryClientInterceptor(LogClientInterceptorMixin,
                                base.UnaryClientInterceptor):
    """Logger interceptor for unary client"""

    PRE_REQUEST_MESSAGE = "gRPC unary client call started"
    POST_REQUEST_MESSAGE = "gRPC unary client call finished"

    def intercept_unary(self, continuation, client_call_details, request):
        return self.intercept(continuation, client_call_details, request)


class LogStreamClientInterceptor(LogClientInterceptorMixin,
                                 base.StreamClientInterceptor):
    """Logger interceptor for streaming client"""

    PRE_REQUEST_MESSAGE = "gRPC streaming client call started"
    POST_REQUEST_MESSAGE = "gRPC streaming client call finished"

    def intercept_stream(self, continuation, client_call_details, request):
        return self.intercept(continuation, client_call_details, request)


class LogServerInterceptorMixin(LogInterceptorMixin):
    """Logger interceptor for server

    This server interceptor is actually never called directly by gRPC, but
    it is always wrapped by `lookout.sdk.interceptors.base.ServerInterceptorWrapper`.
    See its documentation to understand the reason why.

    """
    KIND = "server"
    PRE_REQUEST_MESSAGE = "gRPC server call started"
    POST_REQUEST_MESSAGE = "gRPC server call finished"

    def intercept_service(self, continuation, handler_call_details):
        log_fields = LogFields.from_metadata(
            dict(handler_call_details.invocation_metadata or {}))

        self.add_request_log_fields(
            log_fields, handler_call_details)

        out = continuation(handler_call_details)

        # wraps each gRPC method independently the type, the correct one
        # is ensured to be called by the wrapper.
        return out._replace(
            unary_unary=self._build_wrapper(log_fields, out.unary_unary),
            unary_stream=self._build_wrapper(log_fields, out.unary_stream),
            stream_unary=self._build_wrapper(log_fields, out.stream_unary),
            stream_stream=self._build_wrapper(log_fields, out.stream_stream),
        )

    def _build_wrapper(self, log_fields, original):

        def wrapper(original, *args, **kwargs):
            start = datetime.utcnow()

            self._log_fn(log_fields, self.PRE_REQUEST_MESSAGE)
            err = None
            try:
                resp = original(*args, **kwargs)
            except Exception as exc:
                err = exc
                raise err
            else:
                return resp
            finally:
                self.add_response_log_fields(log_fields, start, err)
                self._log_fn(log_fields, self.POST_REQUEST_MESSAGE)

        if original is None:
            return None

        return functools.partial(wrapper, original)


class LogUnaryServerInterceptor(LogServerInterceptorMixin,
                                base.UnaryServerInterceptor):
    """Logger interceptor for unary server"""

    PRE_REQUEST_MESSAGE = "gRPC unary server call started"
    POST_REQUEST_MESSAGE = "gRPC unary server call finished"


class LogStreamServerInterceptor(LogServerInterceptorMixin,
                                 base.StreamServerInterceptor):
    """Logger interceptor for streaming server"""

    PRE_REQUEST_MESSAGE = "gRPC streaming server call started"
    POST_REQUEST_MESSAGE = "gRPC streaming server call finished"
