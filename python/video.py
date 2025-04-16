#!/usr/bin/env python

# In this file:
#             - reading frames one by one from the webcam,
#             - displaying frames one by one with mpv.


import crypto

import ffmpeg
import subprocess


width = 640
#width = 1920
#height = 1080
height = 480
FRATE = 25

### Public API.
def capture():
    reader = (
        ffmpeg
        .input('/dev/video0', format='v4l2', r=FRATE, s=f'{width}x{height}')
        .output(
            'pipe:',
            format='h264',
            vcodec='libx264',
            r=FRATE,
            pix_fmt='yuv420p',
            preset='ultrafast',  # lowest compression!
            tune='zerolatency',
            g=1,
            **{'x264-params': 'keyint=1'}
        )
    .run_async(pipe_stdout=True)
    )
    while True:
        yield reader.stdout.read(crypto.MAX_PLAINTEXT_BYTES)


def watch( chunks ):
    mpv = subprocess.Popen(
       ['mpv',
        '--no-cache',
        '--untimed',
        '--no-demuxer-thread',
        '--demuxer-lavf-o=flv_format=h264',
        '--correct-pts=no',  #
        '--container-fps-override=25',  #
        '--opengl-glfinish=yes',  #
        '--opengl-swapinterval=0',  #
        '--vo=xv',  #
        '-'],
        stdin=subprocess.PIPE
    )
    for chunk in chunks:
        mpv.stdin.write(chunk)


def test():
    watch( capture() )


if __name__ == '__main__':
    test()
