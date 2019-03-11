import json
import functools
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

from typing import Optional, Tuple, List, Any, Union, Dict

import grpc

LOG_FIELDS_KEY_META = "log-fields"
grpc_max_msg_size = 100 * 1024 * 1024  # 100MB

ClientInterceptor = Union[
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
]


def create_channel(
        target: str,
        options: Optional[List[Tuple[str, Any]]] = None,
        interceptors: Optional[List[ClientInterceptor]] = None,
) -> grpc.Channel:
    """Creates a gRPC channel

    The gRPC channel is created with the provided options and intercepts each
    invocation via the provided interceptors.

    The created channel is configured with the following default options:
        - "grpc.max_send_message_length": 100MB,
        - "grpc.max_receive_message_length": 100MB.

    :param target: the server address.
    :param options: optional list of key-value pairs to configure the channel.
    :param interceptors: optional list of client interceptors.
    :returns: a gRPC channel.

    """
    # The list of possible options is available here:
    # https://grpc.io/grpc/core/group__grpc__arg__keys.html
    options = (options or []) + [
        ("grpc.max_send_message_length", grpc_max_msg_size),
        ("grpc.max_receive_message_length", grpc_max_msg_size),
    ]
    interceptors = interceptors or []
    channel = grpc.insecure_channel(target, options)
    return grpc.intercept_channel(channel, *interceptors)


def create_server(
        max_workers: int,
        options: Optional[List[Tuple[str, Any]]] = None,
        interceptors: Optional[List[grpc.ServerInterceptor]] = None,
) -> grpc.Server:
    """Creates a gRPC server

    The gRPC server is created with the provided options and intercepts each
    incoming RPCs via the provided interceptors.

    The created server is configured with the following default options:
        - "grpc.max_send_message_length": 100MB,
        - "grpc.max_receive_message_length": 100MB.

    :param max_workers: the maximum number of workers to use in the underlying
        futures.ThreadPoolExecutor to be used by the Server to execute RPC
        handlers.
    :param options: optional list of key-value pairs to configure the channel.
    :param interceptors: optional list of server interceptors.
    :returns: a gRPC server.

    """
    # The list of possible options is available here:
    # https://grpc.io/grpc/core/group__grpc__arg__keys.html
    options = (options or []) + [
        ("grpc.max_send_message_length", grpc_max_msg_size),
        ("grpc.max_receive_message_length", grpc_max_msg_size),
    ]
    interceptors = interceptors or []
    return grpc.server(ThreadPoolExecutor(max_workers=max_workers),
                       options=options, interceptors=interceptors)


def to_grpc_address(target: str) -> str:
    """Converts a standard gRPC target to one that is supported by grpcio

    :param target: the server address.
    :returns: the converted address.

    """
    u = urlparse(target)
    if u.scheme == "dns":
        raise ValueError("dns:// not supported")

    if u.scheme == "unix":
        return "unix:"+u.path

    return u.netloc


def wrap_context(func):
    """Wraps the provided servicer method by passing a wrapped context

    The context is wrapped using `lookout.sdk.grpc.utils.WrappedContext`.

    :param func: the servicer method to wrap_context
    :returns: the wrapped servicer method

    """
    @functools.wraps(func)
    def wrapper(self, request, context):
        return func(self, request, WrappedContext(context))

    return wrapper


class WrappedContext:
    """Context wrapper that exposes utilities to handle log fields"""

    def __init__(self, context):
        """Initialzes the wrapped context with the provided original context"""
        self._context = context
        self._invocation_metadata = dict(context.invocation_metadata())
        self._log_fields = LogFields.from_metadata(self._invocation_metadata)

    def __getattr__(self, attr: str):
        """Proxies every attr to the underlying context"""
        return getattr(self._context, attr)

    @property
    def log_fields(self) -> Dict[str, Any]:
        """Returns the log fields"""
        return self._log_fields.fields

    def add_log_fields(self, fields: Dict[str, Any]):
        """Add the provided log fields

        If a key is already present, then it is ignored.

        :param fields: the log fields to add

        """
        self._log_fields.add_fields(fields)

    def pack_metadata(self) -> List[Tuple[str, Any]]:
        """Packs the log fields and the invocation metadata into a new metadata

        The log fields are added in the new metadata with the key
        `LOG_FIELDS_KEY_META`.

        """
        metadata = [(k, v) for k, v in self._invocation_metadata.items()
                    if k != LOG_FIELDS_KEY_META]
        metadata.append((LOG_FIELDS_KEY_META, self._log_fields.dumps()))
        return metadata


class LogFields:
    """Log fields handler

    Provides utilities for log fields serialization and deserialization, and
    to read and add them.

    """
    def __init__(self, fields: Optional[Dict[str, Any]] = None):
        self._fields = fields or {}

    @classmethod
    def from_metadata(cls, metadata: Dict[str, Any]) -> 'LogFields':
        """Initialize the log fields from the provided metadata

        The log fields are taken from the `LOG_FIELDS_KEY_META` key of the
        provided metadata.

        """
        return cls(fields=json.loads(metadata.get(LOG_FIELDS_KEY_META, '{}')))

    @property
    def fields(self) -> Dict[str, Any]:
        """Returns the log fields"""
        return self._fields

    def add_fields(self, fields):
        """Add the provided log fields

        If a key is already present, then it is ignored.

        :param fields: the log fields to add

        """
        for k, v in fields.items():
            if k not in self._fields:
                self._fields[k] = v

    def dumps(self) -> str:
        """Dumps the log fields into a JSON string"""
        return json.dumps(self._fields)
