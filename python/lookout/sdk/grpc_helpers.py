import functools
import json


LOG_FIELDS_KEY_META = "log-fields"


def wrap_context(func):
    @functools.wraps(func)
    def wrapper(self, request, context):
        return func(self, request, WrappedContext(context))
    return wrapper


class WrappedContext:

    def __init__(self, context):
        self._context = context
        self._invocation_metadata = dict(context.invocation_metadata())
        self._log_fields = json.loads(self._invocation_metadata.get(
            LOG_FIELDS_KEY_META, '{}'))

    def __getattr__(self, attr):
        return getattr(self._context, attr)

    @property
    def log_fields(self):
        return self._log_fields

    def add_log_fields(self, fields):
        for k, v in fields.items():
            if k not in self._log_fields:
                self._log_fields[k] = v

    def pack_metadata(self):
        metadata = [(k, v) for k, v in self._invocation_metadata.items()
                    if k != LOG_FIELDS_KEY_META]
        metadata.append((LOG_FIELDS_KEY_META, json.dumps(self._log_fields)))
        return metadata
