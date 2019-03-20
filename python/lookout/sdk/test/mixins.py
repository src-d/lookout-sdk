import socket
from contextlib import closing


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


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
