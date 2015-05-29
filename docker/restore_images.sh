#!/bin/bash
# This script will load into the tar.gz files as images.


[ $# -lt 1 ] && echo "Please specify the dir path of the gz files" && exit 0;

for gz in `ls $1` ; do 
  [[ ${gz#*.} == "tar.gz" ]] && echo "Loading $gz back to images"; 
  sudo docker load < $gz
done
