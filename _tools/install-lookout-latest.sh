#!/bin/bash
#
# Installs latest lookout SDK binary

OS="$(uname | tr '[:upper:]' '[:lower:]')"
LATEST_TAG="$(git ls-remote -t --refs https://github.com/src-d/lookout \
  | sed -E 's/^.+refs\/tags\/(.+)/\1/g' \
  | grep -e '^v[0-9]\+\.[0-9]\+\.[0-9]\+$' \
  | sort \
  | tail -n 1)"

# validate that tag is correct
if [ -z "$LATEST_TAG" ]; then
  echo "can not get the latest tag" >&2
  exit 2
fi

BINARY_URL="https://github.com/src-d/lookout/releases/download/${LATEST_TAG}/lookout-sdk_${LATEST_TAG}_${OS}_amd64.tar.gz"

if ! wget $BINARY_URL ; then
  echo "Unable to download lookout release archive" >&2
  exit 2
fi

if ! tar -xvzf lookout-sdk_*.tar.gz ; then
  echo "Unable to extract lookout release archive" >&2
  exit 2
fi

if ! mv lookout-sdk_*/lookout-sdk ./lookout-sdk ; then
  echo "Unable to move lookout-sdk binary file" >&2
  exit 2
fi

rm -rf lookout-sdk_*
