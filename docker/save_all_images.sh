#!/bin/sh
# This script will save all your local Docker images as tar.gz files.

echo "Checking your images"

for img in `sudo docker images | awk '$1 != "REPOSITORY" { print $1 }' | sort | uniq` ; do
    zip_file=${img//\//_}.tar.gz
    echo "Saving $img to ${zip_file}"
    sudo docker save $img | gzip >  ${zip_file}
done

echo "Save all images into local gz files done."
echo "You can restore them as images using docker load *.tar.gz."
