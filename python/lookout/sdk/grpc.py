from urllib.parse import urlparse

import grpc

grpc_max_msg_size = 100 * 1024 * 1024  # 100MB


def create_channel(target, options=None):
    options = (options or []) + [
        ("grpc.max_send_message_length", grpc_max_msg_size),
        ("grpc.max_receive_message_length", grpc_max_msg_size),
    ]
    return grpc.insecure_channel(target, options)


def to_grpc_address(target):
    """
    converts a standard gRPC target name to a one that is supported by grpcio.
    """

    u = urlparse(target)
    if u.scheme == "dns":
        raise ValueError("dns:// not supported")

    if u.scheme == "unix":
        return "unix:"+u.path

    return u.netloc
