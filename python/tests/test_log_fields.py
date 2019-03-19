import json
import unittest

from grpc.beta._metadata import _Metadatum as Metadatum

from lookout.sdk.grpc.log_fields import LogFields, LogFieldsContext, \
    LOG_FIELDS_KEY_META


class ContextMock:

    def __init__(self, metadata):
        self._metadata = metadata

    def invocation_metadata(self):
        return self._metadata


class TestLogFieldsContext(unittest.TestCase):

    sample_metadata = (
        Metadatum(key="outer_k1", value="v1"),
        Metadatum(key="outer_k2", value=2),
        Metadatum(key="outer_k3", value=True),
        Metadatum(key=LOG_FIELDS_KEY_META,
                  value='{"k1": "v1", "k2": 2, "k3": true}'),
    )

    def test_add_log_fields(self):
        lfc = LogFieldsContext(ContextMock(self.sample_metadata))
        lfc.add_log_fields({"k1": "v1", "w": 3})
        self.assertEqual(lfc.log_fields,
                         {"k1": "v1", "k2": 2, "k3": True, "w": 3})

    def test_pack_metadata(self):
        lfc = LogFieldsContext(ContextMock(self.sample_metadata))
        actual = lfc.pack_metadata()
        expected = [("outer_k1", "v1"), ("outer_k2", 2), ("outer_k3", True),
                    (LOG_FIELDS_KEY_META, '{"k1": "v1", "k2": 2, "k3": true}')]

        self.assertCountEqual(actual, expected)


class TestLogFields(unittest.TestCase):

    def test_initialization(self):
        lf = LogFields()
        self.assertEqual(lf.fields, {})

        fields = {"k1": "v1", "k2": 2, "k3": True}
        lf = LogFields(fields=fields)
        self.assertEqual(lf.fields, fields)

    def test_initialization_from_metadata(self):
        metadata = {
            "outer_k1": "v1",
            "outer_k2": 2,
            "outer_k3": True,
        }
        lf = LogFields.from_metadata(metadata)
        self.assertEqual(lf.fields, {})

        metadata = {
            "outer_k1": "v1",
            "outer_k2": 2,
            "outer_k3": True,
            LOG_FIELDS_KEY_META: '{"k1": "v1", "k2": 2, "k3": true}'
        }
        fields = {"k1": "v1", "k2": 2, "k3": True}
        lf = LogFields.from_metadata(metadata)
        self.assertEqual(lf.fields, fields)

    def test_add_fields(self):
        lf = LogFields()
        lf.add_fields({"k1": "v1", "w": 3})
        self.assertEqual(lf.fields, {"k1": "v1", "w": 3})

        fields = {"k1": "v1", "k2": 2, "k3": True}
        lf = LogFields(fields=fields)
        lf.add_fields({"k1": "y", "w": 3})
        self.assertEqual(lf.fields, {"k1": "v1", "k2": 2, "k3": True, "w": 3})

    def test_serialization(self):
        lf = LogFields()
        self.assertEqual(json.loads(lf.dumps()), {})

        fields = {"k1": "v1", "k2": 2, "k3": True}
        lf = LogFields(fields=fields)
        self.assertEqual(json.loads(lf.dumps()),
                         {"k1": "v1", "k2": 2, "k3": True})
