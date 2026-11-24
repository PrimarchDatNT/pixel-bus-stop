"""Minimal ComfyUI API client (MSI laptop via SSH tunnel on localhost:8188).

    from tools.comfy import gen
    paths = gen("prompt...", out_dir, name="bus", w=1344, h=768, seed=1,
                control=("depth.png", 0.65), init=("plate.png", 0.55), upscale=True, batch=2)
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

HOST = "http://127.0.0.1:8188"
CKPT = "animagine-xl-4.0-opt.safetensors"
CNET = "xinsir-union-sdxl-promax.safetensors"
UPSCALER = "RealESRGAN_x4plus_anime_6B.pth"

QUALITY = "masterpiece, high score, great score, absurdres"
NEG = ("lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, fewer digits, cropped, "
       "worst quality, low quality, low score, bad score, average score, signature, watermark, username, blurry, "
       "jpeg artifacts, sketch, monochrome, deformed, ugly")


def _req(path: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
    r = urllib.request.Request(HOST + path, data=data, headers=headers or {})
    with urllib.request.urlopen(r, timeout=600) as f:
        return f.read()


def upload(path: str | Path) -> str:
    path = Path(path)
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode() + path.read_bytes() + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    res = json.loads(_req("/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return res["name"]


def workflow(prompt: str, neg: str, w: int, h: int, seed: int, steps: int, cfg: float, batch: int,
             control: tuple | None, init: tuple | None, upscale: bool, sampler: str, scheduler: str,
             ckpt: str = CKPT, loras: tuple = (), quality: str | None = QUALITY) -> dict:
    g: dict = {}
    n = iter(range(1, 1000))

    def node(cls, **inputs):
        k = str(next(n))
        g[k] = {"class_type": cls, "inputs": inputs}
        return k

    ck = node("CheckpointLoaderSimple", ckpt_name=ckpt)
    model, clip = [ck, 0], [ck, 1]
    for lname, lw in loras:
        lo = node("LoraLoader", model=model, clip=clip, lora_name=lname, strength_model=lw, strength_clip=lw)
        model, clip = [lo, 0], [lo, 1]
    pos = node("CLIPTextEncode", text=f"{prompt}, {quality}" if quality else prompt, clip=clip)
    ng = node("CLIPTextEncode", text=neg, clip=clip)
    p_out, n_out = [pos, 0], [ng, 0]
    if control:
        img_name, strength = control[0], control[1]
        ctype = control[2] if len(control) > 2 else "depth"
        end = control[3] if len(control) > 3 else 0.8
        cn = node("ControlNetLoader", control_net_name=CNET)
        cnt = node("SetUnionControlNetType", control_net=[cn, 0], type=ctype)
        im = node("LoadImage", image=img_name)
        ap = node("ControlNetApplyAdvanced", positive=p_out, negative=n_out, control_net=[cnt, 0], image=[im, 0],
                  strength=strength, start_percent=0.0, end_percent=end, vae=[ck, 2])
        p_out, n_out = [ap, 0], [ap, 1]
    if init:
        li = node("LoadImage", image=init[0])
        sc = node("ImageScale", image=[li, 0], upscale_method="lanczos", width=w, height=h, crop="center")
        enc = node("VAEEncode", pixels=[sc, 0], vae=[ck, 2])
        lat = [node("RepeatLatentBatch", samples=[enc, 0], amount=batch), 0]
        denoise = init[1]
    else:
        lat = [node("EmptyLatentImage", width=w, height=h, batch_size=batch), 0]
        denoise = 1.0
    ks = node("KSampler", model=model, seed=seed, steps=steps, cfg=cfg, sampler_name=sampler, scheduler=scheduler,
              positive=p_out, negative=n_out, latent_image=lat, denoise=denoise)
    img = [node("VAEDecode", samples=[ks, 0], vae=[ck, 2]), 0]
    if upscale:
        um = node("UpscaleModelLoader", model_name=UPSCALER)
        up = node("ImageUpscaleWithModel", upscale_model=[um, 0], image=img)
        img = [node("ImageScaleBy", image=[up, 0], upscale_method="lanczos", scale_by=0.5), 0]  # 4x -> 2x
    node("SaveImage", images=img, filename_prefix="busstop")
    return g


def gen(prompt: str, out_dir: str | Path, name: str, w: int = 1344, h: int = 768, seed: int = 0, steps: int = 28,
        cfg: float = 5.0, batch: int = 1, neg: str = NEG, control: tuple | None = None, init: tuple | None = None,
        upscale: bool = False, sampler: str = "euler_ancestral", scheduler: str = "normal",
        ckpt: str = CKPT, loras: tuple = (), quality: str | None = QUALITY) -> list[Path]:
    """Run one job; control/init are (local_path, strength[, type, end]) / (local_path, denoise)."""
    if control:
        control = (upload(control[0]), *control[1:])
    if init:
        init = (upload(init[0]), init[1])
    wf = workflow(prompt, neg, w, h, seed, steps, cfg, batch, control, init, upscale, sampler, scheduler,
                  ckpt, loras, quality)
    pid = json.loads(_req("/prompt", json.dumps({"prompt": wf, "client_id": "busstop"}).encode(),
                          {"Content-Type": "application/json"}))["prompt_id"]
    while True:
        h_ = json.loads(_req(f"/history/{pid}"))
        if pid in h_:
            break
        time.sleep(1.5)
    outs = []
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    k = 0
    for node_out in h_[pid]["outputs"].values():
        for im in node_out.get("images", []):
            q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im["subfolder"], "type": im["type"]})
            p = out_dir / f"{name}_{seed}_{k}.png"
            p.write_bytes(_req(f"/view?{q}"))
            outs.append(p)
            k += 1
    return outs
