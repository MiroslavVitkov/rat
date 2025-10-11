#!/usr/bin/env python

# In this file:
#             - reading frames one by one from the webcam,
#             - displaying frames one by one with mpv.


import ffmpeg
import re
import subprocess
import threading
import time

from impl import conf
from impl import crypto


def get_default_audio_device():
    """
    Try to detect the first ALSA capture device using `arecord -l`.
    Returns a string like 'hw:1,0' or None if not found.
    """
    try:
        out = subprocess.check_output(["arecord", "-l"], text=True, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    # Match lines like: "card 1: Device [USB Audio], device 0: USB Audio"
    m = re.search(r"card (\d+): .*device (\d+):", out)
    if not m:
        return None

    card, dev = m.groups()
    return f"hw:{card},{dev}"


def stream( stop_event: threading.Event=threading.Event()
          , camera: str=conf.get()['video']['camera'] ) -> None:
    '''  '''
    if not conf.get()['video']['enable']:
        return

    reader = (
        ffmpeg
        .input(camera,
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


def watch( chunks: [bytes]
         , stop_event: threading.Event=threading.Event() ):
    '''  '''
    if not conf.get()['video']['enable']:
        return

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
        stdin=subprocess.PIPE
    )

    for chunk in chunks:
        if stop_event.is_set():
            break
        mpv.stdin.write(chunk)

    mpv.terminate()


def test():
    if not conf.get()['video']['enable']:
        print('prot/video.py: UNIT TESTS SKIPPED')
        return


    e = threading.Event()
    threading.Thread( target=watch, args=(stream(e), e) ).start()
    time.sleep(5)
    e.set()

    print('prot/video.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
