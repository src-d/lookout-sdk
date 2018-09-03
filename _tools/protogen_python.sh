#!/bin/bash -e
#
# Generates Protobuf + gRCP for Python
# Assumes grpcio_tools package is installed (it includes binary of protoc+grpc plugin)


src_dir="proto"
out_dir="lookout_sdk"

mkdir -p "${out_dir}"

python3 -m grpc_tools.protoc -I "${src_dir}" \
    --python_out="${out_dir}" --grpc_python_out="${out_dir}" \
    "${src_dir}"/*.proto

# because of https://github.com/bblfsh/client-python/blob/bc807c772079f0fb78fe35709fb7b99283f8b539/setup.py#L179
# this also makes depending on "bblfsh" at runtime mandatory :/
find "${out_dir}" -name '*.py' -exec sed -i 's/^from github/from bblfsh.github/g' {} \;
find "${out_dir}" -name '*.py' -exec sed -i "s/import_module('gopkg.in/import_module('bblfsh.gopkg.in/g" {} \;
touch "${out_dir}"/__init__.py
