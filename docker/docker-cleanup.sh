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



# Cleanup exited/dead containers
EXITED_CONTAINERS="`docker ps -a -q -f status=exited -f status=dead | xargs echo`"
if [ "$EXITED_CONTAINERS" != "" ]; then
	echo "Delete all stopped containers..."
	docker rm -v $EXITED_CONTAINERS
	echo "Delete all stopped containers...Done"
fi

UNTAGGED_IMAGES="`docker images -q -f dangling=true | xargs echo`"
if [ "$UNTAGGED_IMAGES" != "" ]; then
	echo "Delete all untagged images"
	docker rmi $UNTAGGED_IMAGES
	echo "Delete all untagged images...Done"
fi
