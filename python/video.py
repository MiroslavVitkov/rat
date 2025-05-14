#!/usr/bin/env python

# In this file:
#             - reading frames one by one from the webcam,
#             - displaying frames one by one with mpv.


import ffmpeg
import subprocess
import threading
import time

import conf
import crypto


def capture( stop_event: threading.Event ):
    '''  '''
    reader = (
        ffmpeg
        .input('/dev/video0',
               format='v4l2',
               r=conf.get()['video']['fps'],
               s=conf.get()['video']['res'])
        .output(
            'pipe:',
            format='h264',
            vcodec='libx264',
            r=conf.get()['video']['fps'],
            pix_fmt='yuv420p',
            preset='ultrafast',  # lowest compression!
            tune='zerolatency',
            g=1,
            **{'x264-params': 'keyint=1'}
        )
    .run_async(pipe_stdout=True)
    )

    while not stop_event.is_set():
        yield reader.stdout.read(crypto.MAX_PLAINTEXT_BYTES)

    reader.stdout.close()
    reader.wait()


def watch( chunks: [bytes], stop_event: threading.Event ):
    '''  '''
    mpv = subprocess.Popen(
       ['mpv',
        '--no-cache',
        '--untimed',
        '--no-demuxer-thread',
        '--demuxer-lavf-o=flv_format=h264',
        '--correct-pts=no',  #
        '--container-fps-override=25', # warn
        '--opengl-glfinish=yes',  #
        '--opengl-swapinterval=0',  #
        '--vo=xv',  # warn
        '-'],
        stdin=subprocess.PIPE
    )

    for chunk in chunks:
        if stop_event.is_set():
            break
        mpv.stdin.write(chunk)

    mpv.terminate()


def test():
    e = threading.Event()
    threading.Thread( target=watch, args=(capture(e), e) ).start()
    time.sleep(12)
    e.set()


if __name__ == '__main__':
    test()
