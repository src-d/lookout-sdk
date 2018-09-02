#!/bin/sh -ex

src_dir="proto"
out_dir="lookout_sdk"

mkdir -p "${out_dir}"
#mkdir -p "${tmp_dir}"
#cp "$src_dir"/*.proto "${tmp_dir}"

#find "${tmp_dir}" -name '*.proto' -exec sed -i '/"google/! {/\//! s/import "/import "lookout_sdk\//g}' {} \;
python3 -m grpc_tools.protoc -I "${src_dir}" \
    --python_out="${out_dir}" --grpc_python_out="${out_dir}" \
    "${src_dir}"/*.proto

find "${out_dir}" -name '*.py' -exec sed -i 's/^from github/from bblfsh.github/g' {} \;
find "${out_dir}" -name '*.py' -exec sed -i "s/import_module('gopkg.in/import_module('bblfsh.gopkg.in/g" {} \;
touch "${out_dir}"/__init__.py

#rm -rf "${tmp_dir}"