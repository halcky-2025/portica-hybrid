import base64
import json
from os import mkdir
import shutil
import subprocess
import os
import sys
import platform
if not os.path.exists('temp'):
    os.mkdir('temp')
order = json.loads(input())
options = order.get('options', None)
fps = options.get('fps', None)
max_frames = options.get('max_frames', None)
tasks = options.get('tasks', None)
for i in tasks.keys():
    filename = tasks[i]['output']
    n = int(i) + 1
    shutil.copyfile('app/static/' + filename, f'temp/in_{n:04}.png')
mp4_path = "temp/out.mp4"
if platform.system() == 'Windows':
    ffmpeg = "projects/sd_movie/sd_movie/ffmpeg/bin/ffmpeg"
else:
    ffmpeg = "ffmpeg"
# make video
cmd = [
    ffmpeg,
    "-y",
    "-vcodec",
    "png",
    "-framerate",
    str(fps),
    "-i",
    os.path.abspath('temp/in_%04d.png'),
    #"-vframes",
    #str(max_frames),
    "-vcodec",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-r",
    "30",
    mp4_path
]
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if process.returncode != 0:
    print(stderr)
    raise RuntimeError(stderr)

with open(mp4_path, 'rb') as f:
    content = base64.b64encode(f.read()).decode('utf-8')
    print(json.dumps({'output_type': 'mov', 'output': content, 'name': 'a.mp4'}))
shutil.rmtree("temp")


