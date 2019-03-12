from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

from typing import Optional, Tuple, List, Any, Union

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
