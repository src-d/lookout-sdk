#!/bin/bash
#
# Checks Protobuff compiler version. 
# If absent, installs one in protoc_dir from GH release.

PROTOC_VER="3.6.0"
OS="$(uname)"
if [[ "$OS" == "Darwin" ]]; then
	protoc_os="osx"
else
	protoc_os="linux"
fi

protoc_dir="../protoc"

cur_ver="$("$protoc_dir/bin/protoc" --version | grep -o '[^ ]*$')"
if [[ "$cur_ver" == "$PROTOC_VER" ]]; then
	echo "Using protoc version $cur_ver"
else
	echo "Installing protoc version $PROTOC_VER"
	protoc_zip="protoc-$PROTOC_VER-$protoc_os-x86_64.zip"
	url="https://github.com/google/protobuf/releases/download/v$PROTOC_VER/$protoc_zip"

	mkdir -p "$protoc_dir"
	wget "$url" -O "$protoc_dir/$protoc_zip"
	if [[ "$?" -ne 0 ]]; then
		echo "Failed to download protoc release from $url"
		exit 2
	fi
	pwd
	find "$protoc_dir"
	unzip -d "$protoc_dir" "$protoc_dir/$protoc_zip"
	if [[ "$?" -ne 0 ]]; then
		echo "Failed to unzip release archive from $protoc_dir/$protoc_zip"
		exit 2
	fi
	rm "$protoc_dir/$protoc_zip"
fi
