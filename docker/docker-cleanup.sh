#!/bin/bash
# A Docker host clean up scripts from yeasy.github.io
# This script will
#  1. delete all stopped containers
#  2. delete all untagged/dangling images


if [ ! -e "/var/run/docker.sock" ]; then
    echo "Cannot find docker socket(/var/run/docker.sock), exit now!"
    exit 1
fi

if docker version >/dev/null; then
    echo "docker is running properly"
else
    echo "Cannot run docker command, exit now!"
    exit 1
fi

echo "Delete all stopped containers..."
docker rm $(docker ps -a -q)
echo "Delete all stopped containers...Done"

echo "Delete all untagged images"
docker rmi $(docker images -q -f dangling=true)
echo "Delete all untagged images...Done"
