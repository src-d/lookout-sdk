#!/bin/bash
#
# Generates Protobuf + gRCP for Golang
# Assumes 'protoc' and 'protoc-gen-gogofaster' binaries are installed in local './protoc/bin' dir

PROTOC="./protoc/bin/protoc"
GOGOFASTER="./protoc/bin/protoc-gen-gogofaster"
sdk="lookout/sdk"
src="proto"
dst="golang"

[[ -f $PROTOC ]] >/dev/null 2>&1 || { echo "Protobuf compiler is required but not found in ${PROTOC}" >&2; exit 1; }

[[ -f $GOGOFASTER ]] >/dev/null 2>&1 || { echo "protoc-gen-gogofaster is required but not found in ${GOGOFASTER}" >&2; exit 1; }

if ! mkdir -p "${dst}" ; then
    echo "Failed to create ${dst}"
    exit 2
fi

# 'protoc-gen-gogofaster' must be under $PATH to be found by 'protoc'
export PATH=./protoc/bin:$PATH

"${PROTOC}" -I proto \
    --gogofaster_out=plugins=grpc,\
Mgoogle/protobuf/any.proto=github.com/gogo/protobuf/types,\
Mgoogle/protobuf/duration.proto=github.com/gogo/protobuf/types,\
Mgoogle/protobuf/timestamp.proto=github.com/gogo/protobuf/types,\
Mgoogle/protobuf/struct.proto=github.com/gogo/protobuf/types,\
Mgoogle/protobuf/wrappers.proto=github.com/gogo/protobuf/types:"${dst}" \
"${src}/${sdk}/"*.proto
if [[ "$?" -ne 0 ]]; then
    echo "Failed to run protoc on ${src}/${sdk}"
    exit 2
fi

if ! mv "${dst}/${sdk}/"*.go pb ; then
    echo "Failed to mv ${dst}/${sdk}/*.go to ./pb"
    exit 2
fi

if ! rm -rf "${dst}" ; then
    echo "Failed to delete ${dst}"
    exit 2
fi
