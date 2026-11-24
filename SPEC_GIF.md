# Style v4 — "GIF" pixel art (style bible for the styleframe)

Target look: `refs/pinterest_pixel_shop.gif` (800×600, native pixel = 2 px → 400×300 logical). Clean, hand-placed
pixel art: orthographic front elevation, pastel daylight, flat fills with 2–3 tones, crisp edges, readable little
details (a shopkeeper reading a newspaper, labelled shelves, window glare), and small looping motion (petals, flags,
a cat, birds). Extract a few frames and LOOK at them before drawing and while reviewing your work:

    .venv/bin/python -c "from PIL import Image; im=Image.open('refs/pinterest_pixel_shop.gif'); im.seek(0); im.convert('RGB').save('/tmp/gif0.png')"

Our subject: a Hanoi bus stop whose roof is overgrown by a magenta bougainvillea (hoa giấy), next to an old-quarter
Hanoi shophouse, summer noon (season "hạ"). The blocking mock is `assets/out_gif/_mock/mock3@5x.png` (drawn from `tools/layout_gif.py`).

## Composition (rev B, after the client compared attempt A with the GIF)
Attempt A (a row of 5 pastel tube houses + many props, archived in `assets/out_gif_a/`) was judged less artistic than
the GIF: no focal point, everything small and competing, flat values. Rev B follows the GIF's structure:
- ONE hero building, big (about half the frame), slightly darker and richer in value than the sky so the pink pops.
- ONE hero bloom mass (the bougainvillea) as large and characterful as the GIF cherry tree.
- Breathing room: open sky on top and to the right; pale low-contrast distance (city + Long Biên bridge).
- Props only at the feet, few and iconic. Saturated colour is reserved for the bloom; signs are muted.

## Canvas, tools, geometry
- Logical canvas **384×216**, rendered at integer **×5** → 1920×1080. Never draw sub-pixels.
- Toolkit: `from tools.px_gif import *` (same API as `tools/px.py`: `new, rect, line, poly, ellipse, put, paste,
  outline, flip, recolor, text, text_size, validate, save_asset`). Colours by name: `c("bl")`. Palette: `PALETTE_GIF`
  in `tools/px_gif.py`. `validate()` rejects off-palette colours and semi-transparent pixels.
- All positions: `from tools.layout_gif import *`. Read it first.
- `text()` draws a small pixel font with Vietnamese diacritics (see `tools/px.py`); real Vietnamese words on signs.

## Rendering rules (what makes the GIF look good)
1. **Orthographic front elevation.** No vanishing points. Tops of horizontal things (balcony slabs, roof parapets,
   window sills, the sidewalk) show as a 1–2 px lighter band; undersides as a 1–2 px shade band.
2. **Light from the upper-left.** Every material uses 3–4 tones from its ramp: 1 px highlight on top/left edges,
   base fill, shade on the right/bottom and under overhangs, darkest tone for crevices.
3. **Outlines:** architecture uses 1 px dark frames (`wood_k` / `ink`) like the dark-brown frames in the GIF.
   Characters and animals get NO dark outline: their shape is made by flat colour blocks (see Characters).
   Never pure black. Background haze objects get no outline.
4. **Flat and clean.** No noise, no random speckle, no dithering patterns, no gradients except a few flat bands in
   the sky. Every pixel cluster must be deliberate. Big flat areas are fine (the GIF sky is one colour).
5. **Readable details at 1–3 px:** window glare = 2–3 short diagonal `white` / `glass_l` strokes; shutters = vertical
   slats with a highlight column; potted plants = small leaf clumps; railings = 1 px bars; signs with real text.
6. **Foliage and blossom as clusters:** rounded clumps 4–9 px with a highlight on the upper-left, shade on the
   lower-right, darker gaps between clumps, a ragged silhouette with 1 px bumps, a few loose petals or leaves at the
   edge. Study the GIF cherry tree closely: that is the bar for the bougainvillea and the tree.
7. **Pastel and harmonious.** Saturated colours only for the hero bougainvillea, signs, the red plastic stools and the
   bus. Distant things use the `haze*` colours and less contrast.
8. **Scale:** adult 30 px tall with a big ~9 px head (about 3.5 heads, cute like the GIF people). Cat loaf 14×9,
   dog lying 24×11. Cub motorbike 34×20.

## Characters (rules taken from the GIF's people and animals)
- Big round head, ~3.5 heads tall; front or 3/4 view for static people; simple calm poses.
- Face = flat skin + two 1×2 px dark eyes (or closed-eye dashes), maybe 1 px blush. No nose, mouth, brows, beard.
- Hair is one clean solid shape with a 1–2 px highlight band. Clothes are flat 2 tones (base + shade on one side).
- 3–5 colours per figure, no outline, no stray pixels, smooth pixel-perfect curves (no doubled corners).
- Animals: simple silhouette, 2–3 colours, dot eye; no fur stripes or noise (one or two stripe marks at most).
9. **No baked ground shadows or glows** on sprites; the compositor adds soft shadows. Animation loops are small:
   2–4 frames at 3–6 fps for idles and sway, 6 frames at 8 fps for walks, 4 frames for particles.

## Deliverables and format
- Export with `save_asset(group, name, frames, fps=..., anchor=..., states=..., notes=...)`. It writes
  `assets/out_gif/<group>/<name>.png` (horizontal frame strip), `.json` and `_preview/` (×5 PNG + GIF).
- **Scenery layers** (groups `env`, `shelter`): full-canvas frames **384×216**, transparent where empty,
  `anchor=(0, 0)`, so the compositor stacks them 1:1.
- **Actors and props** (group `actors`): cropped frames, `anchor` = feet / contact point, and in `MANIFEST.md`
  give the suggested canvas position of each anchor.
- Each group writes `assets/out_gif/<group>/MANIFEST.md`: layer name, z-order hint, frames/fps, placement, notes.
- Put scripts in `assets/src_gif/<group>/`. Check your work by compositing it over `assets/out_gif/_mock/mock.png`
  (or the other groups' real layers if they already exist) and viewing at ×3–×5 next to a GIF crop.
