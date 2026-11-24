# Style v2 — "32-bit glossy" (client feedback round 3)

The client finds v1 too flat and wants the look of late-90s 32-bit console sprite art (they cite
Mega Man X4): glossy, voluminous, "looks 3D". **Match the rendering qualities only — never copy any
game's characters, art or assets.** Subject matter stays our Hanoi bus-stop scene.

## What makes that look (targets for every asset)
1. **Big, rich ramps.** 7–10 tones per material, hue-shifted (shadows toward blue/purple, highlights
   toward warm yellow-white), saturation peaking in the mid-tones. Gradients are hand-placed bands,
   not dither noise. Free colour choice (no global 45-colour lock), but ≤ 32 colours per sprite.
2. **Form shading like a lit 3D object.** Cylinders/spheres/bevelled boxes read as volumes: a
   clear terminator, core shadow, then **bounce light** (warm, from the ground) on the lower shadow edge.
3. **Specular hot spots.** 1–3 px near-white highlights on glossy materials (car paint, chrome,
   glass, plastic seats, lantern lacquer, wet asphalt, cat's eyes and nose).
4. **Rim light.** A thin cool sky-coloured edge on the side away from the key light.
5. **Horizon reflections on gloss.** Car bodies, bus windows, chrome: upper band reflects the sky
   (light), a sharp darker "horizon" line, lower band reflects the ground (dark) — the classic 90s
   chrome look. Glass gets 1–2 diagonal glare streaks.
6. **Coloured selective outlines.** Outline = darkest tone of the adjacent material, broken or
   lightened on the lit side; inner lines separate panels/parts; manual anti-aliasing on curves.
7. **Saturated, confident colour** with clean silhouettes. No muddy greys.

Key light: upper-left-front (sun) · rim/back light: cool sky blue from upper-right-back ·
bounce: warm from below.

## Technical
* Canvas **640×360 @3×** — geometry in `tools/layout_v2.py`. Adult ≈ 40 px, bus 226×70,
  foreground cat 64×40, shelter 160 px wide.
* PNG RGBA, alpha 0/255 only, hard pixels (no AA blur, no semi-transparency).
* Style-test outputs go to `assets/out_v2/<track>/` (track = `render3d` or `shade25d`), with a
  `styleframe.png` test frame (640×360, 1×) + `styleframe@3x.png`.

## Style-test frame (same for both tracks so the client can compare)
640×360. Sky gradient (summer noon). A facade strip of 3–4 Hanoi tube houses across the back
(bottom at y=216; shop signs, balconies, AC units, water tanks). Far sidewalk + road + near sidewalk
bands per layout_v2. The **bus shelter with plastic seats and the bougainvillea in full summer
bloom** centred at x≈292. **Bus (facing left, driver side, no passenger doors on this side)** in the
far lane at x≈548, partly cut by the right edge. **Orange tabby cat** sitting on the near sidewalk at
x≈150. One adult waiting in the shelter (optional).
