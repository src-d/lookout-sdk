#!/bin/bash
#
# Runs bblfsh server in CI

set -e

docker run -d --name bblfshd --privileged -v $HOME/bblfshd:/var/lib/bblfshd -p "9432:9432" bblfsh/bblfshd:v2.9.2
docker exec -it bblfshd bblfshctl driver install --force go bblfsh/go-driver:v2.4.0
