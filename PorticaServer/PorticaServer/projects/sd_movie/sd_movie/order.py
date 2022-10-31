from datetime import time
import os
import subprocess
from base64 import standard_b64encode
import json

import numpy as np
import pandas as pd
import threading

import encodings.idna
import time

class Parameter:
    def __init__(self):
        self.post_id = None
        self.secret = None
        self.prompt = "a painting of a virus monster playing guitar";
        self.W = 512;
        self.H = 512;
        self.scale = 7.5
        self.strength = 0.75
        self.n_iter = 1
        self.ckpt = "models/ldm/stable-diffusion-v1/sd-v1-4.ckpt"
        self.plms = False
        self.ddim_steps = 50
        self.max_frames = 90
        self.zoom_series = {}
        self.angle_series = {}
        self.translation_x_series = {}
        self.translation_y_series = {}
        self.fps = 15
        self.init_video = None
        self.plms = ""
        self.contrast_series = {}
        self.noise_series = {}
        self.strength_series = {}
        self.scale_series = {}
        self.seed_series = {}

def main( ) :
    """Run a single prediction on the model"""
    ppar = json.loads(input())
    # sanity checks:

    # load default args
    anim_args = Parameter()
    anim_args.post_id = int(ppar.get('post_id', None))
    anim_args.secret = ppar.get('secret', '')
    options = ppar.get('options', {})
    anim_args.fps = int(options.get('fps', None))
    anim_args.max_frames = int(options.get('max_frames', None))
    animation_prompts = parse_key_frames(ppar.get('prompt', None), str)

    # animations use key framed prompts
    animation_prompts = animation_prompts

    prompt_series = pd.Series([np.nan for a in range(anim_args.max_frames)])
    for i, prompt in animation_prompts.items():
        prompt_series[i] = prompt
    prompt_series = prompt_series.ffill().bfill()
    anim_args.prompt_series = prompt_series
    anim_args.init_img = options.get('init_img', None)

    # overwrite with user input
    if anim_args.max_frames:
        anim_args.angle_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('angle', None), int))
        anim_args.zoom_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('zoom', None), float))
        anim_args.translation_x_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('translation_x', None), int), True)
        anim_args.translation_y_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('translation_y', None), int), True)
        anim_args.noise_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('noise', None), float))
        anim_args.strength_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('strength', None), float))
        anim_args.contrast_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('contrast', None), float))
        anim_args.seed_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('seed', None), int), True)
        anim_args.scale_series = get_inbetweens(anim_args.max_frames, parse_key_frames(options.get('scale', None), float))
    seed = options.get('seed', None)
    anim_args.seed = seed
    anim_args.plms = options.get("plms", '')
    
    anim_args.init_video = options.get('init_video', None)
    if anim_args.init_video is None:
        render_animation(anim_args)
    else:
        render_input_video(anim_args)

    # make video

def parse_key_frames(string, typo):
    i = 0
    v = ''
    att = 'non'
    values = []
    while i < len(string):
        c = string[i]
        if '0' <= c and c <= '9':
            v += c
            if att != 'let': att = 'num'
            i += 1
            continue
        elif c == ' ':
            v += c
            i += 1
            continue
        elif c == '|':
            values.append({'ope': c})
        elif c == ':':
            values.append({'ope': c})
        else:
            v += c
            att = 'let'
            i += 1
            continue
        if att == 'num' or att == 'let':
            values.insert(len(values) - 1, {'ope': att, 'val': v})
        v = ''
        i += 1
    if att == 'num' or att == 'let':
        values.append({'ope': att, 'val': v})
    i = 0
    fn = 0
    vals = {}
    while True:
        if i < len(values):
            val = values[i]
            if val['ope'] == 'num':
                if i + 1< len(values):
                    val2 = values[i + 1]
                    if val2['ope'] == ':':
                        i += 2
                        fn = int(val2['val'])
        if i < len(values):
            val = values[i]
            i += 1
            if val['ope'] == 'let' or val['ope'] == 'num':
                vals[fn] = typo(val['val'])
                fn += 1
            else:
                return
        else:
            return
        if i < len(values):
            val = values[i]
            i += 1
            if val['ope'] == '|':
                i += 0
            else:
                return
        else:
            return vals


def get_inbetweens(max_frames, key_frames, integer=False):
    key_frame_series = pd.Series([np.nan for a in range(max_frames)])

    for i, value in key_frames.items():
        key_frame_series[i] = value
    key_frame_series = key_frame_series.astype(float)

    interp_method = "Linear"

    key_frame_series[0] = key_frame_series[key_frame_series.first_valid_index()]
    key_frame_series[max_frames - 1] = key_frame_series[key_frame_series.last_valid_index()]
    key_frame_series = key_frame_series.interpolate(
        method=interp_method.lower(), limit_direction="both"
    )
    if integer:
        return key_frame_series.astype(int)
    return key_frame_series
def send(args):
    import urllib3
    http = urllib3.PoolManager()
    r = http.request('POST', 'http://localhost:5000/task', fields = args)
    v = r.data.decode('utf-8')
    o = json.loads(v)
def render_animation(anim_args):
    first = True
    threads = []
    fitst = True
    for frame_idx in range(anim_args.max_frames):
        # apply transforms to previous frame
        angle = str(anim_args.angle_series[frame_idx])
        zoom = str(anim_args.zoom_series[frame_idx])
        translation_x = str(anim_args.translation_x_series[frame_idx])
        translation_y = str(anim_args.translation_y_series[frame_idx])
        noise = str(anim_args.noise_series[frame_idx])
        strength = str(anim_args.strength_series[frame_idx])
        contrast = str(anim_args.contrast_series[frame_idx])
        prompt = anim_args.prompt_series[frame_idx]
        seed = str(anim_args.seed_series[frame_idx] + frame_idx)
        scale = str(anim_args.scale_series[frame_idx])
        plms = anim_args.plms
        args = {'post_type': 'sd_movie', 'post_id': anim_args.post_id, 'secret': anim_args.secret, 'prompt': prompt, 'angle': angle, 'zoom': zoom, 'translation_x': translation_x, 'translation_y': translation_y, 'noise': noise, 'strength': strength, 'W': anim_args.W, 'H': anim_args.H, 'key': str(frame_idx), 'order': str(frame_idx), 'sample': 'True', 'seed': seed, 'scale': scale, 'plms': plms}
        if first and anim_args.init_img:
            args['init_img'] = {}
            with open('app/static/' + anim_args.init_img['address'], 'rb') as f:
                content = f.read()
                extension = os.path.splitext(anim_args.init_img['address'])[1].lower()
                if extension == '.jpg':
                    mime = 'image/jpeg'
                elif extension == '.jpeg':
                    mime = 'image/jpeg'
                elif extension == '.png':
                    mime = 'image/png'
                args['init_img'] =  (anim_args.init_img['address'], content, mime)
        first = False
        t = threading.Thread(target=send, args=(args,))
        t.start()
        time.sleep(0.05)
        threads.append(t)
    
    for t in threads:
        t.join()
    print(json.dumps({'count': anim_args.max_frames}))

def render_input_video(anim_args):
    os.mkdir("temp")
    # create a folder for the video input frames to live in
    try:
        for f in pathlib.Path(video_in_frame_path).glob("*.jpg"):
            f.unlink()
    except:
        pass
    vf = r"select=not(mod(n\," + str(anim_args.extract_nth_frame) + "))"
    if platform.system() == 'Windows':
        ffmpeg = "projects/sd_movie/sd_movie/ffmpeg/bin/ffmpeg"
    else:
        ffmpeg = "ffmpeg"
    subprocess.run(
        [
            ffmpeg,
            "-i",
            f"{anim_args.init_video}",
            f"-r {{anim_args.fps}}"
            f"{anim_args.init_video}"])
    subprocess.run(
        [
            ffmpeg,
            "-i",
            f"{anim_args.init_video}",
            "-vcodec",
            "mjpeg",
            "temp/in%05d.jpg",
        ],
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")
    
    for frame_idx in range(anim_args.max_frames):
        # apply transforms to previous frame
        angle = str(anim_args.angle_series[frame_idx])
        zoom = str(anim_args.zoom_series[frame_idx])
        translation_x = str(anim_args.translation_x_series[frame_idx])
        translation_y = str(anim_args.translation_y_series[frame_idx])
        noise = str(anim_args.noise_series[frame_idx])
        strength = str(anim_args.strength_series[frame_idx])
        contrast = str(anim_args.contrast_series[frame_idx])
        prompt = anim_args.prompt_series[frame_idx]
        args = {'aitype': 'sd_movie', 'post_id': anim_args.post_id, 'secret': anim_args.secret, 'prompt': prompt, 'angle': angle, 'zoom': zoom, 'translation_x': translation_x, 'translation_y': translation_y, 'noise': noise, 'strength': strength, 'init_img': '@1', 'W': anim_args.W, 'H': anim_args.H, 'key': frame_idx, 'init_video': 'true', 'order': str(frame_idx), 'sample': True}
        with open(f"temp/in{frame_idx:05}.jpg", "rb") as f:
            upload_img = f.read()
        args['output'] = ('init_img', upload_img, 'image/jpeg')
        import urllib3
        http = urllib3.PoolManager()
        r = http.request('POST', 'http://localhost:5000/task', fields = args)
        o = json.loads(r.data.decode('utf-8'))
    print(json.dumps({'count': anim_args.max_frames}))
    os.rmdir("temp")





def next_seed(args):
    if args.seed_behavior == "iter":
        args.seed += 1
    elif args.seed_behavior == "fixed":
        pass  # always keep seed the same
    else:
        args.seed = random.randint(0, 2**32)
    return args.seed
main()