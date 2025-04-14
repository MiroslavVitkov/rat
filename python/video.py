#!/usr/bin/env python

# In this file: reading frames one by one from the webcam.


import ffmpeg


### Public API.

# cb(frame) - called on each frame
def run(cb):
    return None


### Details.
width = 640
height = 480
PIX_FMT='yuv420p'
RESOLUTION = '{}x{}'.format(width, height)

FORMAT = 'rawvideo'
#FORMAT = 'h264'


reader = (
    ffmpeg
    .input('/dev/video0', s=RESOLUTION)
    .output('pipe:', format=FORMAT, pix_fmt=PIX_FMT)
    .run_async(pipe_stdout=True)
)


writer = (
    ffmpeg
    .input('pipe:', format=FORMAT, pix_fmt=PIX_FMT, s=RESOLUTION)
    .output('/tmp/kur.mp4', format='h264')
    .overwrite_output()
    .run_async(pipe_stdin=True)
)


while True:
    frame = reader.stdout.read(width * height * 3)
    print(len(frame))
    writer.stdin.write(frame)
