# Style v3 — lofi anime, AI plates + AI sprites, motion in code

Approved by the client 22/11/2026: "lean" lofi anime look, 16:9, hazy Hanoi tube houses behind the trees.
Reference frame: `assets/out_v2/ai/lofi/lofi_h_hr_111_0.png`. Earlier styles (v1 procedural pixel, v2 shade25d / Blender)
were rejected; their files stay for reference only.

## Infrastructure
- ComfyUI on the MSI laptop (`<user>@<msi-host>`, Windows/PowerShell, `D:\AI\ComfyUI`, Animagine XL 4.0,
  ControlNet `xinsir-union-sdxl-promax`, RealESRGAN anime upscaler). Start it detached:
  `ssh <user>@<msi-host> '$cmd = "cmd /c D:\AI\ComfyUI\.venv\Scripts\python.exe D:\AI\ComfyUI\main.py --listen 127.0.0.1 --port 8188 --preview-method none > D:\AI\comfyui.log 2>&1"; Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$cmd; CurrentDirectory="D:\AI\ComfyUI"}'`
- Tunnel: `ssh -f -N -o ExitOnForwardFailure=yes -L 8188:127.0.0.1:8188 <user>@<msi-host>`; client `tools/comfy.py`.
- Prompt fragments: `tools/style_v3.py`.

## Background plates (`assets/out_v3/plates/`)
- `night_rain.png` — canonical layout. Built by `assets/src_v3/plates/houses_layer.py` (tube-house facades cut out of
  the retro AI frame, sky removed, fog graded) + `compose_night.py` (houses pasted into the approved frame's sky,
  baked rain streaks removed, img2img 0.5 + tile ControlNet unify). No rain in the plate: rain is animated in code.
- Season/time variants: `variants.py <key> <seed> [dn1] [dn3] --comp`
  1. canny of the night plate (+ crisp house edges, no road reflections) locks the layout; img2img 0.88 from a
     brightened night plate;
  2. our tube-house layer is pasted back where the night plate shows houses (Animagine otherwise draws Japanese
     wooden houses), skipping foliage;
  3. unify pass: img2img 0.42 + tile ControlNet.
  The house row is therefore identical in every season.

## Sprites (`assets/out_v3/sprites/`)
- Prompt = `<subject tags>, SPRITE_STYLE, SPRITE`. Never use `STYLE` for sprites: its palette words turned every vehicle green.
- Colours as weighted tags, e.g. `(yellow city bus:1.3)`.
- Bus: img2img 0.72+ from the v2 bus scaled ×5 and blurred (`assets/src_v3/sprites/style_test.py`).
- Motorbikes: "riding scooter, sitting" (not "step-through", which gives kick scooters).
- Cut out with rembg (`isnet-general-use` / `isnet-anime`), trimmed RGBA, plus `manifest.json` per group.
