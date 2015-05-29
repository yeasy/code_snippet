#!/bin/sh
# This script will save all your local Docker images as tar.gz files.

for img in `docker images | awk '$1 != "REPOSITORY" { print $1 }' | sort | uniq` ; do echo $img ; docker save $img | gzip – > $img.tar.gz ; done
