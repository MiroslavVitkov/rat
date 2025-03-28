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


reader = (
    ffmpeg
    .input('/dev/video0', s='{}x{}'.format(width, height))
    .output('pipe:', format='rawvideo', pix_fmt='yuv420p')
    .run_async(pipe_stdout=True)
)


writer = (
    ffmpeg
    .input('pipe:', format='rawvideo', pix_fmt='yuv420p', s='{}x{}'.format(width, height))
    .output('/tmp/kur.mp4', format='h264', pix_fmt='yuv420p')
    .overwrite_output()
    .run_async(pipe_stdin=True)
)


while True:
    frame = reader.stdout.read(width * height * 3)
    print(len(frame))
    writer.stdin.write(frame)
