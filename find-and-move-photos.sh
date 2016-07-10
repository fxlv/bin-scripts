#!/bin/bash
# find and move photos based on date

DESTINATION_FOLDER=~/OneDrive/photos

function usage (){
    echo "Usage"
    echo
    echo "$0 < date >"
    echo
    echo "For example:"
    echo "$0 2015-08-07"
    echo
    exit 0
}

function main () {
    DATE_FROM=$1
    DATE_TO=$(date -j -v +1d -f "%Y-%m-%d" $DATE_FROM "+%Y-%m-%d")
    YEAR=$(echo $DATE_FROM | cut -d "-" -f 1)
    DEST=$DESTINATION_FOLDER/$YEAR/$DATE_FROM/
    echo "Finding all photos created on $DATE_FROM -> $DATE_TO and moving them to $DEST"
    find . -type f -name "*.jpg" -newermt $DATE_FROM ! -newermt $DATE_TO -exec ls -lash {} \;
    read -p "Shall I continue, sir? (y/n) " yesno
    if [ $yesno == "y" ];then
        echo "Executing"
        if [ ! -d $DEST ]; then
            echo "The destination directory does not exist, creating"
            mkdir $DEST
        else 
            echo "Destination directory exists, good."
        fi
        find . -type f -name "*.jpg" -newermt $DATE_FROM ! -newermt $DATE_TO -exec mv -v {} $DEST \;
    else
        echo "Aborting"
    fi
}

if [ $# -eq 1 ]; then
    main $1
else
    usage
fi
