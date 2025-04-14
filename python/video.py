#!/usr/bin/env python

# In this file:
#             - reading frames one by one from the webcam,
#             - displaying frames one by one with mpv.


import ffmpeg
import subprocess


### Public API.

# cb(frame) - called on each frame
#def run(cb):
#    return None


### Details.
width = 640
height = 480


reader = (
    ffmpeg
    .input('/dev/video0', format='v4l2', s=f'{width}x{height}')
    .output('pipe:', format='h264', vcodec='libx264', pix_fmt='yuv420p')
    .run_async(pipe_stdout=True)
)


mpv = subprocess.Popen(
    ['mpv', '--no-cache', '--untimed', '--demuxer-lavf-o=flv_format=h264', '-'],
    stdin=subprocess.PIPE
)


with open('/tmp/kur.h264', 'wb') as out_file:
    while True:
        chunk = reader.stdout.read(4096)
        print(len(chunk))
        out_file.write(chunk)
        mpv.stdin.write(chunk)
