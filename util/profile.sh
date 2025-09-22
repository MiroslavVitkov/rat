#!/usr/bin/env bash


# In this file: time the steps of the video pipeline.


#../python/video.py test > /tmp/log


# $1 - tag in the log
# $2 - fname to write
function extract
{
    grep "$1" /tmp/log | cut -f1 -d' ' | sed '/V:/d' > /tmp/"$2"
}


extract CAP cap
extract REC rec
extract SHOWN shown

./plot.py /tmp/cap /tmp/rec /tmp/shown
