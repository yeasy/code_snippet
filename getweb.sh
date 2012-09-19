#!/bin/bash
# This simple script can mirror a website to local directory.
# Feel free to distribute or modify the code.:)
# Version: 0.3
# Author: Baohua Yang@THU
# Created: May 27, 2011
# Updated: Aug 18, 2011
# Usage:
# getweb [-d save_dir] <website> 
#   save_dir is current defaultly

SAVE_DIR="$PWD" #defaultly save to current directory
URL="www.google.com"
AGENT="Mozilla/5.0"
OPTION=""
OPTION+=" -x" #Create a hierarchy of directories
OPTION+=" -nH" #Disable generation of host-prefixed directories
OPTION+=" -m" #Mirroring, turns on recursion and time-stamping, infinite recursion depth
OPTION+=" -p" #Download media type files
OPTION+=" -k" #Convert links locally
OPTION+=" -c" #Continue downloading with previous files
OPTION+=" -nv" #Turn off verbose
OPTION+=" -np" #No try parent directory
#OPTION+=" -L" #Follow relative links only
OPTION+=" -t 3" #Try times
#OPTION+=" --html-extension" #For dynamic pages
#echo $OPTION

while getopts d: opt
do
    case "$opt" in
      d)  SAVE_DIR="$OPTARG"
          ;;
      \?)
      echo "Usage: $0 [-d save_dir] website_url"
      exit;;
    esac
done

test ! -d $SAVE_DIR && mkdir $SAVE_DIR
test ! -w $SAVE_DIR && echo "[Error]: Save directory isn't writeable." && exit 1
shift `expr $OPTIND - 1` && URL=$1
wget -e robots=off $OPTION -U $AGENT -P $SAVE_DIR $URL
echo "Done!"
