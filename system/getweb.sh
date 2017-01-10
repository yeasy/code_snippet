#!/bin/bash
# This simple script can mirror a website to local directory.
# Feel free to distribute or modify the code.:)
# Version: 0.3
# Author: Baohua Yang@THU
# Created: May 27, 2011
# Updated: Dec 20, 2016
# Usage:
# getweb.sh [-d save_dir] WEBSITE_URL
# save_dir is current path by default

SAVE_DIR="$PWD" #defaultly save to current directory
URL=""
AGENT="Mozilla/5.0"

OPTION="-e robots=off"  # Not tell a robot
OPTION+=" -x" # Create a hierarchy of directories
OPTION+=" -nH" # Disable generation of host-prefixed directories
OPTION+=" -m" # Mirroring, turns on recursion and time-stamping, infinite recursion depth
OPTION+=" -p" # Download media type files
OPTION+=" -k" # Convert links locally
OPTION+=" -c" # Continue downloading with previous files
OPTION+=" -nv" # Turn off verbose
OPTION+=" -np" # No try parent directory
#OPTION+=" -L" # Follow relative links only
OPTION+=" -t 3" # Try times
#OPTION+=" -E" # For dynamic pages, will add html suffix for js/asp...
OPTION+=" -U $AGENT"  # Set agent header

#echo $OPTION

command -v wget >/dev/null 2>&1 || { echo >&2 "wget is not installed. Please install it first."; exit 1; }

while getopts d: opt
do
    case "$opt" in
      d)  SAVE_DIR="$OPTARG"
          ;;
      h)  echo "Usage: $0 [-d save_dir] WEBSITE_URL"
      exit;;
      \?)
      echo "Usage: $0 [-d save_dir] WEBSITE_URL"
      exit;;
    esac
done

test ! -d ${SAVE_DIR} && echo "save_dir ${SAVE_DIR} not exists, will create it..." && mkdir -p ${SAVE_DIR} && echo "save_dir ${SAVE_DIR} is created"
test ! -w ${SAVE_DIR} && echo "[Error]: save_dir isn't writeable, will exit." && exit 1
OPTION+=" -P ${SAVE_DIR}"

shift `expr $OPTIND - 1` && URL=$1
[ -z "$URL" ] && echo "URL is not given, will exit." && exit 1

# Run wget cmd with options
echo "=== Start getting the website $URL"
wget $OPTION $URL

echo "=== Done! The website is saved to ${SAVE_DIR}"
