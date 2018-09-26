#!/bin/bash
#
# Installs latest lookout SDK binary
# Depends on GNU grep
set -x

#TODO(bzz): check for local cached version first

OS="$(uname | tr '[:upper:]' '[:lower:]')"

oIFS=$IFS IFS=' '
curl -v ${GITHUB_TOKEN:+'-H' "Authorization: token $GITHUB_TOKEN"} \
    --connect-timeout 5 \
    --max-time 10 \
    --retry 5 \
    --retry-delay 0 \
    --retry-max-time 40\
    "https://api.github.com/repos/src-d/lookout/releases/latest" \
  | tee -a ./lookout-install.log \
  | grep -oP '"browser_download_url": "\K(.*)(?=")' \
  | grep "${OS}" \
  | wget -qi -

if [[ "${PIPESTATUS[0]}" -ne 0 || \
      "${PIPESTATUS[1]}" -ne 0 || \
      "${PIPESTATUS[2]}" -ne 0 || \
      "${PIPESTATUS[3]}" -ne 0 || \
      "${PIPESTATUS[4]}" -ne 0 ]];
then
  echo "Unable download latest lookout SDK release" >&2
  exit 2
fi
IFS=$oIFS; unset -v oIFS
# http://mywiki.wooledge.org/BashFAQ/050#I_only_want_to_pass_options_if_the_runtime_data_needs_them

if ! tar -xvzf lookout-sdk_*.tar.gz ; then
  echo "Unable to extract lookout release archive" >&2
  exit 2
fi

if ! mv lookout-sdk_*/lookout-sdk ./lookout-sdk ; then
  echo "Unable to move lookout-sdk binary file" >&2
  exit 2
fi

rm -rf lookout-sdk_*
