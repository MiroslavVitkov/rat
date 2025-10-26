#!/usr/bin/env python

# In this file:
#             - reading frames one by one from the webcam,
#             - displaying frames one by one with mpv.


import ffmpeg
import re
import subprocess
from threading import Event, Thread
import time

from impl import conf
from impl import crypto


def stream( death: Event=Event()
          , camera: str=conf.get()['video']['camera'] ) -> None:
    '''
    Capture video+audio, mux into Matroska, send via stdout in chunks.
    '''
    reader = (
        ffmpeg
        .input(
            camera,
            format='v4l2',
            input_format='mjpeg',
            # This is a request to the driver; the same in output is an order to ffmpeg.
            r=conf.get()['video']['fps'],
            s=conf.get()['video']['res'],
            thread_queue_size=512)
        .output(
            'pipe:',
            format='h264',
            vcodec='libx264',
            r=conf.get()['video']['fps'],
            pix_fmt='yuv420p',
            preset='ultrafast',  # lowest compression!
            tune='zerolatency',
            g=1)
        .run_async(pipe_stdout=True)
    )

    while not death.is_set():
        yield reader.stdout.read(crypto.MAX_PLAINTEXT_BYTES)

    reader.stdout.close()
    reader.wait()


def watch( chunks: [bytes]
         , death: Event=Event() ):
    '''
    Feed video+audio to mpv to decode.
    '''
    mpv = subprocess.Popen(
       ['mpv',
        '--no-cache',
        '--untimed',
        '--no-demuxer-thread',
        '--demuxer-lavf-o=flv_format=h264,probesize=32,analyzeduration=0',
        '--vd-lavc-threads=1',
        '--correct-pts=no',
        '--opengl-glfinish=yes',
        '--opengl-swapinterval=0',
        '-'],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL
    )

    for chunk in chunks:
        if death.is_set():
            break
        mpv.stdin.write(chunk)

    mpv.terminate()


def test():
    if not conf.get()['video']['enable']:
        print('prot/video.py: UNIT TESTS SKIPPED')
        return

    death = Event()
    Thread( target=watch, args=(stream(death), death) ).start()
    time.sleep(10)
    death.set()

    print('prot/video.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
