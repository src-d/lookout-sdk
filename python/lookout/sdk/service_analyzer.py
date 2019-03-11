import re
import inspect
from lookout.sdk import service_analyzer_pb2_grpc
from lookout.sdk.grpc.utils import wrap_context


class AnalyzerServicerMetaclass(type):
    """Metaclass for analyzer servicer

    This metaclass is used to simplify the api of the user-defined analyzers
    and to provide pythonic api on top of gRPC.

    See `lookout.sdk.service_analyzer.AnalyzerServicer`.

    """
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
    """Base analyzer servicer to be extended by the user

    The user that wants to create a custom analyzer has to extend this class
    and to implement the following methods:
        - notify_review_event,
        - notify_push_event.

    Both methods have the following signature:

        method(self, request, context)

    where `request` is the gRPC request and context is an instane of
    `pb.WrappedContext`.

    Internals:
        gRPC still invokes the `NotifyReviewEvent` and `NotifyPushEvent`
        methods that are automatically generated. The `AnalyzerServicerMetaclass`
        metaclass makes each gRPC method call the corresponding method with the
        same name, but written in snake case. Each gRPC method instead of
        passing the gRPC original context, they pass a wrapped one using
        `lookout.sdk.grpc.utils.WrappedContext`.

    """
    pass
