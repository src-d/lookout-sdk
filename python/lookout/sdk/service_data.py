from lookout.sdk import service_data_pb2_grpc


class DataStub:

    def __init__(self, channel):
        self._data_stub = service_data_pb2_grpc.DataStub(channel)

    def get_changes(self, context, request, timeout=None, metadata=None,
                    credentials=None, wait_for_ready=None):
        metadata = self._build_metadata(context, metadata)
        return self._data_stub.GetChanges(
            request, timeout=timeout, metadata=metadata,
            credentials=credentials, wait_for_ready=wait_for_ready
        )

    def get_files(self, context, request, timeout=None, metadata=None,
                  credentials=None, wait_for_ready=None):
        metadata = self._build_metadata(context, metadata)
        return self._data_stub.GetFiles(
            request, timeout=timeout, metadata=metadata,
            credentials=credentials, wait_for_ready=wait_for_ready
        )

    def _build_metadata(self, context, metadata):
        new_metadata = context.pack_metadata()
        if metadata:
            new_metadata.extend(metadata)

        return new_metadata
