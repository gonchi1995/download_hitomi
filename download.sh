#!/bin/bash

img_url=galleries/$1/img_url.txt

if [ -e $img_url ]; then
    echo "urllist found."
else
    echo "execute list_url."
    python3 list_url.py $1
fi

echo "execute download."
python3 download.py $1
