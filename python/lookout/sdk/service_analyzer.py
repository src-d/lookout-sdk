import re
import inspect
from lookout.sdk import service_analyzer_pb2_grpc
from lookout.sdk.grpc_helpers import wrap_context


class AnalyzerServicerMetaclass(type):

    servicer = service_analyzer_pb2_grpc.AnalyzerServicer

    def __new__(cls, clsname, bases, dct):
        new_attrs = dct.copy()

        for name, func in inspect.getmembers(
                cls.servicer, predicate=inspect.isroutine):
            if name.startswith("__"):
                continue

            snake_case_name = cls._to_snake_case(name)
            new_attrs[snake_case_name] = dct.get(snake_case_name, func)
            new_attrs[name] = wrap_context(new_attrs[snake_case_name])

        return super(AnalyzerServicerMetaclass, cls).__new__(
            cls, clsname, bases, new_attrs)

    @classmethod
    def _to_snake_case(cls, s):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class AnalyzerServicer(object, metaclass=AnalyzerServicerMetaclass):
    pass
