#!/bin/bash -e
#
# Generates Protobuf + gRCP for Python
# Assumes 'grpcio_tools' package is installed (it includes binary of protoc+grpc plugin)


src_dir="proto"
out_dir="python"

mkdir -p "${out_dir}"

python3 -m grpc_tools.protoc -I "${src_dir}" \
    --python_out="${out_dir}" --grpc_python_out="${out_dir}" \
    $(find "${src_dir}/lookout" -iname "*.proto")

# because these package exist in bblfsh, and are going to be used at runtime
# https://github.com/bblfsh/client-python/blob/bc807c772079f0fb78fe35709fb7b99283f8b539/setup.py#L179
# this also makes "bblfsh" a mandatory runtime dependency
find "${out_dir}" -name '*.py' -exec sed -i 's/^from github/from bblfsh.github/g' {} \;
find "${out_dir}" -name '*.py' -exec sed -i "s/import_module('gopkg.in/import_module('bblfsh.gopkg.in/g" {} \;

# make a python packages
<< END >> "${out_dir}/lookout/__init__.py"
# DO NOT CHANGE OR ADD ANYTHING HERE
import pkg_resources
pkg_resources.declare_namespace(__name__)
__version__ = 0, 0, 1
END
touch "${out_dir}/lookout/sdk/__init__.py"
