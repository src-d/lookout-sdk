import json
import functools

from typing import Optional, Tuple, List, Any, Dict

LOG_FIELDS_KEY_META = "log-fields"


def wrap_context(func):
    """Wraps the provided servicer method by passing a wrapped context

    The context is wrapped using `lookout.sdk.grpc.log_fields.LogFieldsContext`.

    :param func: the servicer method to wrap_context
    :returns: the wrapped servicer method

    """
    @functools.wraps(func)
    def wrapper(self, request, context):
        return func(self, request, LogFieldsContext(context))

    return wrapper


class LogFieldsContext:
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
