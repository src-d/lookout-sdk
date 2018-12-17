#!/bin/bash
#
# Checks protoc-gen-gogofaster installed in local 'protoc_dir' dir.
# If it's absent installs it in 'protoc_dir' from GH release.

GOGO_PROTOBUF_VER=1.2.0

protoc_dir="./protoc"
protoc_bin_dir=${protoc_dir}/bin

gogo_protobuf_release_url=https://github.com/gogo/protobuf/archive/v${GOGO_PROTOBUF_VER}.zip
gogo_protobuf_zip_path=${protoc_dir}/protobuf-${GOGO_PROTOBUF_VER}.zip
gogo_protobuf_base_dir=${protoc_dir}/src/github.com/gogo
gogo_protobuf_src_dir=${gogo_protobuf_base_dir}/protobuf
gogofaster_package=${gogo_protobuf_src_dir}/protoc-gen-gogofaster
gogofaster_bin_path=${protoc_bin_dir}/protoc-gen-gogofaster

# Since 'protoc-gen-gogofaster' does not expose its version, it must be reinstalled
if [[ -f ${gogofaster_bin_path} ]]; then
	echo "Removing old gogofaster ${gogofaster_bin_path}"
	rm ${gogofaster_bin_path}
fi

echo "Installing gogofaster v${GOGO_PROTOBUF_VER}"

mkdir -p ${protoc_bin_dir}
if [[ ! -f ${gogo_protobuf_zip_path} ]]; then
	wget ${gogo_protobuf_release_url} -O ${gogo_protobuf_zip_path}
	if [[ "$?" -ne 0 ]]; then
		echo "Failed to download protoc release from ${gogo_protobuf_release_url}"
		exit 2
	fi
fi

mkdir -p ${gogo_protobuf_base_dir}
unzip -aoq ${gogo_protobuf_zip_path} -d ${gogo_protobuf_base_dir}
if [[ "$?" -ne 0 ]]; then
	echo "Failed to unzip release from ${gogo_protobuf_zip_path}"
	exit 2
else
	rm -rf ${gogo_protobuf_src_dir}
	mv ${gogo_protobuf_src_dir}-${GOGO_PROTOBUF_VER} ${gogo_protobuf_src_dir}
fi

export GOPATH=`pwd`/${protoc_dir}
go build -o ${gogofaster_bin_path} ${gogofaster_package}
if [[ "$?" -ne 0 ]]; then
	echo "Failed to install ${gogofaster_package} into ${gogofaster_bin_path}"
	exit 2
fi

if ! rm -rf "${gogo_protobuf_src_dir}" ; then
    echo "Failed to delete ${gogo_protobuf_src_dir}"
    exit 2
fi