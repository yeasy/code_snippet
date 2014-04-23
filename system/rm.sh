#!/bin/bash
# This scirpt provides a safe way for the 
# linux command 'rm'. It's under GNU license.
# Feel free to distribute or modify the code.:)
# Author: Baohua Yang@THU
# Created: Nov 10, 2010
# Version: 0.1
# Usage: 
#  Put this script to /usr/local/sbin/;
#  Run 'chmod a+x /usr/local/sbin/rm';
#  Enjoy!

TRASH_DIR=".local/share/Trash/files"
#Size of large file which will be deleted permanently
FILE_SIZE_LIMIT=512000

while getopts 'fiIrh' OPT; do
    case $OPT in
        f) #mean force remove
            continue;;
        i) #prompt before every removal
            read -p "Sure to delete? [Y/n] " option
            if [ -n "$option" ] && [ "$option" == "Y" ] || [ "$option" == "y" ]; then
                continue;
            else
                echo "Operation Canceled."
                exit
            fi;;
        I) #mean to rm recursively
            continue;;
        r) #mean to rm recursively
            continue;;
        h) #mean to print help
            echo "This is a simple safe rm script"
            echo "Pls check the source code";;
        ?) #other parameters
            continue;;
    esac
done

#move parameters left
shift $(($OPTIND - 1))
if [ $# -lt 1 ]; then #check if there's destination file
    echo "`which $0`: missing operand"
    echo Try "'rm -h' for more information."
    exit
fi

#check the trash dir
[ -d ~/$TRASH_DIR ] || mkdir -p ~/$TRASH_DIR

for filename in "$@"
do
    if [ -e $filename ]; then #if exist
        size=`du -s $filename | awk '{print $1}'` #get size in KB
        if [ $size -gt $FILE_SIZE_LIMIT ]; then #larger than FILE_SIZE_LIMIT
            read -p "File is too large, delete permanently?[Y/n] " option
            if [ -n "$option" ] && [ "$option" == "Y" ] || [ "$option" == "y" ]; then
                /bin/rm -rf $filename
            else
                echo "Operation canceled"
            fi
        else #no larger than FILE_SIZE_LIMIT
            cp -rf $filename ~/$TRASH_DIR
            /bin/rm -rf $filename
        fi
    else #file not exist
        echo "`which $0`: cannot remove '$filename': No such file or directory"
    fi
done
