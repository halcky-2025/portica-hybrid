import sys
import os
sys.path.append(os.getcwd())
print(sys.path)
import time
import argparse, os, sys, glob
from distutils.command.upload import upload
import json
from dataclasses import fields
from pickle import TRUE
import PIL
import cv2
import torch
import numpy as np
from omegaconf import OmegaConf
from PIL import Image
from tqdm import tqdm, trange
from imwatermark import WatermarkEncoder
from itertools import islice
from einops import rearrange, repeat
from torchvision.utils import make_grid
import time
from pytorch_lightning import seed_everything
from torch import autocast
from contextlib import contextmanager, nullcontext

from ldm.util import instantiate_from_config
from ldm.models.diffusion.ddim import DDIMSampler
from ldm.models.diffusion.plms import PLMSSampler

from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
from transformers import AutoFeatureExtractor

import urllib3
import base64
import random

# load safety model


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def numpy_to_pil(images):
    """
    Convert a numpy image or a batch of images to a PIL image.
    """
    if images.ndim == 3:
        images = images[None, ...]
    images = (images * 255).round().astype("uint8")
    pil_images = [Image.fromarray(image) for image in images]

    return pil_images


def load_model_from_config(config, ckpt, verbose=False):
    print(f"Loading model from {ckpt}")
    pl_sd = torch.load(ckpt, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    model = instantiate_from_config(config.model)
    m, u = model.load_state_dict(sd, strict=False)
    if len(m) > 0 and verbose:
        print("missing keys:")
        print(m)
    if len(u) > 0 and verbose:
        print("unexpected keys:")
        print(u)

    model.cuda()
    model.eval()
    return model


def put_watermark(img, wm_encoder=None):
    if wm_encoder is not None:
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = wm_encoder.encode(img, 'dwtDct')
        img = Image.fromarray(img[:, :, ::-1])
    return img

def load_img(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    print(f"loaded input image of size ({w}, {h}) from {path}")
    w, h = map(lambda x: x - x % 32, (w, h))  # resize to integer multiple of 32
    image = image.resize((w, h), resample=PIL.Image.LANCZOS)
    image = np.array(image).astype(np.float32) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)
    return 2.*image - 1.

def load_replacement(x):
    try:
        hwc = x.shape
        y = Image.open("assets/rick.jpeg").convert("RGB").resize((hwc[1], hwc[0]))
        y = (np.array(y)/255.0).astype(x.dtype)
        assert y.shape == x.shape
        return y
    except Exception:
        return x


class Parameter:
    def __init__(self):
        self.prompt = "a painting of a virus monster playing guitar";
        self.W = 512;
        self.H = 512;
        self.scale = 7.5
        self.init_img = None
        self.strength = 0.75
        self.seed = random.randint(0, 1000)
        self.n_iter = 1
        self.ckpt = "models/ldm/stable-diffusion-v1/sd-v1-4.ckpt"

def main():
    save_path = None
    error = ''
    secret = ''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server",
        type=str,
        nargs="?",
        help="which server ask from",
        default="http://localhost:5000"
    )
    parser.add_argument(
        "--outdir",
        type=str,
        nargs="?",
        help="dir to write results to",
        default="outputs/txt2img-samples"
    )
    parser.add_argument(
        "--skip_grid",
        action='store_true',
        help="do not save a grid, only individual samples. Helpful when evaluating lots of samples",
    )
    parser.add_argument(
        "--skip_save",
        action='store_true',
        help="do not save individual samples. For speed measurements.",
    )
    parser.add_argument(
        "--ddim_steps",
        type=int,
        default=50,
        help="number of ddim sampling steps",
    )
    parser.add_argument(
        "--plms",
        action='store_true',
        help="use plms sampling",
    )
    parser.add_argument(
        "--laion400m",
        action='store_true',
        help="uses the LAION400M model",
    )
    parser.add_argument(
        "--fixed_code",
        action='store_true',
        help="if enabled, uses the same starting code across samples ",
    )
    parser.add_argument(
        "--ddim_eta",
        type=float,
        default=0.0,
        help="ddim eta (eta=0.0 corresponds to deterministic sampling",
    )
    parser.add_argument(
        "--C",
        type=int,
        default=4,
        help="latent channels",
    )
    parser.add_argument(
        "--f",
        type=int,
        default=8,
        help="downsampling factor",
    )
    parser.add_argument(
        "--n_samples",
        type=int,
        default=1,
        help="how many samples to produce for each given prompt. A.k.a. batch size",
    )
    parser.add_argument(
        "--n_rows",
        type=int,
        default=0,
        help="rows in the grid (default: n_samples)",
    )
    parser.add_argument(
        "--from-file",
        type=str,
        help="if specified, load prompts from this file",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/stable-diffusion/v1-inference.yaml",
        help="path to config which constructs model",
    )
    parser.add_argument(
        "--precision",
        type=str,
        help="evaluate at this precision",
        choices=["full", "autocast"],
        default="autocast"
    )
    opt = parser.parse_args()
    while TRUE:
        try:
            par = Parameter();
            seins = secret
            secret = ''
            dic = {'secret': seins}
            if error:
                dic['tag'] = 'error'
                dic['output'] = error
            elif save_path:
                print(2)
                with open(save_path, "rb") as f:
                    upload_img = f.read()
                    save_path = None
                dic['output'] = ('update.png', upload_img, 'image/png')
                dic['tag'] = 'img'
            http = urllib3.PoolManager()
            r = http.request('POST', opt.server + '/order', fields=dic)
            print(r.data.decode('utf-8'))
            o = json.loads(r.data.decode('utf-8'))
            error = ''
            if len(o.get('prompt', '')) == 0:
                time.sleep(1)
                continue
            secret = o.get('secret', '')
            options = o.get('options', None)
            if options:
                model = options.get('model', 'sd1.4')
                if model == "sd1.4":
                    par.ckpt = "models/ldm/stable-diffusion-v1/sd-v1-4.ckpt"
                elif model == 'wd1.2':
                    par.ckpt = 'models/ldm/wd-v1-2.ckpt'
                par.prompt = options.get('en_prompt', '')
                par.W = int(options.get('W', '512'))
                par.H = int(options.get('H', '512'))
                init_img = options.get('init_img', None)
                if init_img:
                    init_img_address = init_img.get('address', 'a.png')
                    init_img_content = init_img.get('content', '')
                    if len(init_img_content) > 0:
                        init_img_content = base64.b64decode(init_img)
                        file_name = 'a' + os.path.splitext(init_img_address)[1].lower()
                        print(file_name)
                        with open(file_name, 'wb') as f:
                            f.write(init_img)
                            par.init_img = file_name
                            par.scale = 5.0
                            par.n_iter = 1
                par.strength = float(options.get('strength', '0.75'))

            if opt.laion400m:
                print("Falling back to LAION 400M model...")
                opt.config = "configs/latent-diffusion/txt2img-1p4B-eval.yaml"
                par.ckpt = "models/ldm/text2img-large/model.ckpt"
                opt.outdir = "outputs/txt2img-samples-laion400m"

            seed_everything(par.seed)

            config = OmegaConf.load(f"{opt.config}")
            model = load_model_from_config(config, f"{par.ckpt}")

            device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
            model = model.to(device)

            if opt.plms:
                sampler = PLMSSampler(model)
            else:
                sampler = DDIMSampler(model)

            os.makedirs(opt.outdir, exist_ok=True)
            outpath = opt.outdir
            if par.init_img is None:
                print("Creating invisible watermark encoder (see https://github.com/ShieldMnt/invisible-watermark)...")
                wm = "StableDiffusionV1"
                wm_encoder = WatermarkEncoder()
                wm_encoder.set_watermark('bytes', wm.encode('utf-8'))

                batch_size = opt.n_samples
                n_rows = opt.n_rows if opt.n_rows > 0 else batch_size
                if not opt.from_file:
                    prompt = par.prompt
                    assert prompt is not None
                    data = [batch_size * [prompt]]

                else:
                    print(f"reading prompts from {opt.from_file}")
                    with open(par.from_file, "r") as f:
                        data = f.read().splitlines()
                        data = list(chunk(data, batch_size))

                sample_path = os.path.join(outpath, "samples")
                os.makedirs(sample_path, exist_ok=True)
                base_count = len(os.listdir(sample_path))
                grid_count = len(os.listdir(outpath)) - 1

                start_code = None
                if opt.fixed_code:
                    start_code = torch.randn([opt.n_samples, opt.C, par.H // opt.f, par.W // opt.f], device=device)

                precision_scope = autocast if opt.precision=="autocast" else nullcontext
                with torch.no_grad():
                    with precision_scope("cuda"):
                        with model.ema_scope():
                            tic = time.time()
                            all_samples = list()
                            for n in trange(par.n_iter, desc="Sampling"):
                                for prompts in tqdm(data, desc="data"):
                                    uc = None
                                    if par.scale != 1.0:
                                        uc = model.get_learned_conditioning(batch_size * [""])
                                    if isinstance(prompts, tuple):
                                        prompts = list(prompts)
                                    c = model.get_learned_conditioning(prompts)
                                    shape = [opt.C, par.H // opt.f, par.W // opt.f]
                                    samples_ddim, _ = sampler.sample(S=opt.ddim_steps,
                                                                     conditioning=c,
                                                                     batch_size=opt.n_samples,
                                                                     shape=shape,
                                                                     verbose=False,
                                                                     unconditional_guidance_scale=par.scale,
                                                                     unconditional_conditioning=uc,
                                                                     eta=opt.ddim_eta,
                                                                     x_T=start_code)

                                    x_samples_ddim = model.decode_first_stage(samples_ddim)
                                    x_samples_ddim = torch.clamp((x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0)
                                    x_samples_ddim = x_samples_ddim.cpu().permute(0, 2, 3, 1).numpy()

                                    x_checked_image = x_samples_ddim

                                    x_checked_image_torch = torch.from_numpy(x_checked_image).permute(0, 3, 1, 2)

                                    if not opt.skip_save:
                                        for x_sample in x_checked_image_torch:
                                            x_sample = 255. * rearrange(x_sample.cpu().numpy(), 'c h w -> h w c')
                                            img = Image.fromarray(x_sample.astype(np.uint8))
                                            img = put_watermark(img, wm_encoder)
                                            img.save(os.path.join(sample_path, f"{base_count:05}.png"))
                                            base_count += 1

                                    if not opt.skip_grid:
                                        all_samples.append(x_checked_image_torch)

                            if not opt.skip_grid:
                                # additionally, save as grid
                                grid = torch.stack(all_samples, 0)
                                grid = rearrange(grid, 'n b c h w -> (n b) c h w')
                                grid = make_grid(grid, nrow=n_rows)

                                # to image
                                grid = 255. * rearrange(grid, 'c h w -> h w c').cpu().numpy()
                                img = Image.fromarray(grid.astype(np.uint8))
                                img = put_watermark(img, wm_encoder)
                                save_path = os.path.join(outpath, f'grid-{grid_count:04}.png')
                                img.save(os.path.join(outpath, f'grid-{grid_count:04}.png'))
                                grid_count += 1

                            toc = time.time()

                print(f"Your samples are ready and waiting for you here: \n{outpath} \n"
                      f" \nEnjoy.")
            else:
                batch_size = opt.n_samples
                n_rows = opt.n_rows if opt.n_rows > 0 else batch_size
                if not opt.from_file:
                    prompt = par.prompt
                    assert prompt is not None
                    data = [batch_size * [prompt]]

                else:
                    print(f"reading prompts from {opt.from_file}")
                    with open(opt.from_file, "r") as f:
                        data = f.read().splitlines()
                        data = list(chunk(data, batch_size))

                sample_path = os.path.join(outpath, "samples")
                os.makedirs(sample_path, exist_ok=True)
                base_count = len(os.listdir(sample_path))
                grid_count = len(os.listdir(outpath)) - 1

                assert os.path.isfile(par.init_img)
                init_image = load_img(par.init_img).to(device)
                init_image = repeat(init_image, '1 ... -> b ...', b=batch_size)
                init_latent = model.get_first_stage_encoding(model.encode_first_stage(init_image))  # move to latent space

                sampler.make_schedule(ddim_num_steps=opt.ddim_steps, ddim_eta=opt.ddim_eta, verbose=False)

                assert 0. <= par.strength <= 1., 'can only work with strength in [0.0, 1.0]'
                t_enc = int(par.strength * opt.ddim_steps)
                print(f"target t_enc is {t_enc} steps")

                precision_scope = autocast if opt.precision == "autocast" else nullcontext
                with torch.no_grad():
                    with precision_scope("cuda"):
                        with model.ema_scope():
                            tic = time.time()
                            all_samples = list()
                            for n in trange(par.n_iter, desc="Sampling"):
                                for prompts in tqdm(data, desc="data"):
                                    uc = None
                                    if par.scale != 1.0:
                                        uc = model.get_learned_conditioning(batch_size * [""])
                                    if isinstance(prompts, tuple):
                                        prompts = list(prompts)
                                    c = model.get_learned_conditioning(prompts)

                                    # encode (scaled latent)
                                    z_enc = sampler.stochastic_encode(init_latent, torch.tensor([t_enc]*batch_size).to(device))
                                    # decode it
                                    samples = sampler.decode(z_enc, c, t_enc, unconditional_guidance_scale=par.scale,
                                                             unconditional_conditioning=uc,)

                                    x_samples = model.decode_first_stage(samples)
                                    x_samples = torch.clamp((x_samples + 1.0) / 2.0, min=0.0, max=1.0)

                                    if not opt.skip_save:
                                        for x_sample in x_samples:
                                            x_sample = 255. * rearrange(x_sample.cpu().numpy(), 'c h w -> h w c')
                                            Image.fromarray(x_sample.astype(np.uint8)).save(
                                                os.path.join(sample_path, f"{base_count:05}.png"))
                                            base_count += 1
                                    all_samples.append(x_samples)

                            if not opt.skip_grid:
                                # additionally, save as grid
                                grid = torch.stack(all_samples, 0)
                                grid = rearrange(grid, 'n b c h w -> (n b) c h w')
                                grid = make_grid(grid, nrow=n_rows)

                                # to image
                                grid = 255. * rearrange(grid, 'c h w -> h w c').cpu().numpy()
                                save_path = os.path.join(outpath, f'grid-{grid_count:04}.png')
                                Image.fromarray(grid.astype(np.uint8)).save(os.path.join(outpath, f'grid-{grid_count:04}.png'))
                                grid_count += 1

                            toc = time.time()

                print(f"Your samples are ready and waiting for you here: \n{outpath} \n"
                      f" \nEnjoy.")
        except ZeroDivisionError as e:
        #except Exception as e:
            error = str(e)


if __name__ == "__main__":
    main()
