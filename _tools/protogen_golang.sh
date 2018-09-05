#!/bin/bash
#
# Generates Protobuf + gRCP for Golang
# Assumes 'protoc' and 'protoc-gen-gogofaster' binaries are installed

PROTOC="../protoc/bin/protoc"

[[ -f "../protoc/bin/protoc" ]] >/dev/null 2>&1 || { echo "Protobuf compiler is required but not found in ${PROTOC}" >&2; exit 1; }

"${PROTOC}" -I proto \
    --gogofaster_out=plugins=grpc,\
Mgoogle/protobuf/any.proto=github.com/gogo/protobuf/types,\
Mgoogle/protobuf/duration.proto=github.com/gogo/protobuf/types,\
Mgoogle/protobuf/timestamp.proto=github.com/gogo/protobuf/types,\
Mgoogle/protobuf/struct.proto=github.com/gogo/protobuf/types,\
Mgoogle/protobuf/wrappers.proto=github.com/gogo/protobuf/types:golang \
proto/lookout/sdk/*.proto
