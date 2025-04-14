#!/usr/bin/env python

# In this file: reading frames one by one from the webcam.


import ffmpeg


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


with open('/tmp/kur.h264', 'wb') as out_file:
    while True:
        chunk = reader.stdout.read(4096)
        print(len(chunk))
        out_file.write(chunk)
#reader.wait()
