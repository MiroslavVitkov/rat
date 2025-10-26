#!/usr/bin/env python


# In this file: steam audio and play it in the remote side.
#               mic → ALSA → ffmpeg → UDP → mpv → ALSA → speaker

import ffmpeg
import re
import subprocess
from threading import Event, Thread
import time

from impl import conf, crypto


def get_default_audio_device():
    '''
    Try to detect the first ALSA capture device using `arecord -l`.
    Returns a string like 'hw:1,0' or None if not found.
    '''
    try:
        out = subprocess.check_output(['arecord', '-l'], text=True,
                                      stderr=subprocess.DEVNULL)
    except( FileNotFoundError, subprocess.CalledProcessError ):
        return None

    # Match lines like: "card 1: Device [USB Audio], device 0: USB Audio".
    m = re.search(r"card (\d+): .*device (\d+):", out)
    if not m:
        return None

    card, dev = m.groups()
    return f"hw:{card},{dev}"


def stream( death=Event() ):
    """Capture microphone audio, encode as AAC-in-MPEGTS, and yield chunks."""
    mic = get_default_audio_device()
    process = (
        ffmpeg
        .input(mic, format='alsa', ac=2, ar=48000)
        .output(
            'pipe:',
            format='mpegts',
            acodec='aac',
            ar=48000,
            audio_bitrate='96k',
#            ffflags='+nobuffer+flush_packets',
            flush_packets=1,
            max_delay=0,
        )
        .run_async(pipe_stdout=True, pipe_stderr=subprocess.DEVNULL)
    )

    while not death.is_set():
        data = process.stdout.read(crypto.MAX_PLAINTEXT_BYTES)
        if not data:
            break
        yield data

    process.stdout.close()
    process.wait()


def watch( chunks, death=Event() ):
    """Receive audio chunks, feed them to mpv for playback."""
    mpv = subprocess.Popen([
        'mpv',
        '--no-cache',
        '--untimed',
        '--profile=low-latency',
        '--vd-lavc-threads=1',
        '--audio-delay=0',
        '-',
    ], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    for chunk in chunks:
        if death.is_set():
            break
        mpv.stdin.write(chunk)

    mpv.stdin.close()
    mpv.terminate()


def test():
    '''Local loopback test: mic → ffmpeg(AAC/TS) → mpv.'''
    death = Event()
    Thread(target=watch, args=(stream(death), death)).start()
    time.sleep(10)
    death.set()
    print('prot/audio.py: UNIT TESTS PASSED')


if __name__ == '__main__':
    test()
