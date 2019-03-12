import functools
import json
from typing import Any, Dict, List, Tuple


LOG_FIELDS_KEY_META = "log-fields"


def wrap_context(func):
    """Wraps the provided servicer method by passing a wrapped context

    The context is wrapped using `lookout.sdk.grpc_helpers.WrappedContext`.

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
        self._log_fields = json.loads(self._invocation_metadata.get(
            LOG_FIELDS_KEY_META, '{}'))

    def __getattr__(self, attr: str):
        """Proxies every attr to the underlying context"""
        return getattr(self._context, attr)

    @property
    def log_fields(self):
        """Returns the log fields"""
        return self._log_fields

    def add_log_fields(self, fields: Dict[str, Any]):
        """Add the provided log fields

        If a key is already present, then it is ignored.

        :param fields: the log fields to add

        """
        for k, v in fields.items():
            if k not in self._log_fields:
                self._log_fields[k] = v

    def pack_metadata(self) -> List[Tuple[str, Any]]:
        """Packs the log fields and the invocation metadata into a new metadata"""
        metadata = [(k, v) for k, v in self._invocation_metadata.items()
                    if k != LOG_FIELDS_KEY_META]
        metadata.append((LOG_FIELDS_KEY_META, json.dumps(self._log_fields)))
        return metadata
