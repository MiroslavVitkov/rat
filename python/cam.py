#!/usr/bin/env python

from ffmpeg.ffmpeg import FFmpeg
FFmpeg().input('/dev/video0').output('/tmp/kur.avi').execute()
