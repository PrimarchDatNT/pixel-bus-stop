"""Style v3 — lofi anime (client-approved 22/11/2026). Shared prompt fragments for every ComfyUI job.

Look: clean "lean" lofi anime illustration — soft cel shading, clean lines, muted teal / deep green palette
with warm yellow accents, atmospheric, uncluttered. Reference frame:
assets/out_v2/ai/lofi/lofi_h_hr_111_0.png (night rain, bus stop with bougainvillea in the centre).

Sprites are generated in NEUTRAL soft daylight on a plain white background; the video code grades them per
scene (night tint, warm lamp light, rain darkening), so never bake night/neon lighting into a sprite.
"""

STYLE = ("lofi anime style, soft cel shading, clean lines, muted teal and green palette with warm accents, "
         "gentle soft lighting, anime coloring, highly detailed, high quality illustration")

# Sprites: same line/shading language but NO palette words — "teal and green palette" tinted every vehicle green
# (23/11 review of the first vehicle batch). Sprite colours come from the subject tags; scene grading does the rest.
SPRITE_STYLE = ("lofi anime style, soft cel shading, clean lines, gentle soft lighting, anime coloring, "
                "highly detailed, high quality illustration")

SPRITE = ("full body, side view, from side, simple background, white background, isolated, centered, "
          "nothing else in the image")

NEG = ("lowres, worst quality, low quality, blurry, text, watermark, signature, username, jpeg artifacts, "
       "3d render, photo, realistic, cropped, out of frame, multiple views, background scenery, ground, floor, "
       "shadow on background, motion lines, speed lines, splash, frame, border")

QUALITY = "masterpiece, high score, great score, absurdres"

# Output sizes in the final 1920x1080 frame (height in px, used to set downscale + composition)
SCALE_1080 = {
    "adult": 120, "child": 85, "cat_fg": 190, "bus": (690, 210), "sedan": (300, 100), "motorbike": (140, 125),
    "bicycle": (150, 130), "bird": 26, "lion": 170, "dragon": (620, 190),
}
