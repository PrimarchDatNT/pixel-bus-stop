# shelter group manifest

**Common canvas:** every shelter layer (all except `stool_red`) is **164x96 px, top-left at scene (136, 84)**
(covers x136..299, y84..179), anchor (0,0). Drop them all at the same position and they line up 1:1.
Frames of animated assets are stored as a horizontal strip (frame i at x = i*164). Scripts: `assets/src/shelter/`
(`structure.py`, `boug.py`, `decor.py`, `composite.py`; `common.py`/`view.py` helpers).

| name | frame size | frames/fps | anchor | layer (Z_ORDER) | scene pos (top-left) | season | notes |
|---|---|---|---|---|---|---|---|
| shelter_back | 164x96 | 1 | (0,0) | shelter_back | (136,84) | all | Rear frame: perforated bay x168-186 + route-map panel, transparent glass bay x189-241, lit Ha Long Bay lightbox x244-274 (y130-168). Feet y168. |
| seats | 164x96 | 1 | (0,0) | seats | (136,84) | all | 4 blue moulded seats on steel rail, seat x=190/202/214/226, feet y171. People sit at x~190-236. |
| stool_red | 10x12 | 1 | bottom-centre | seats (or near_sidewalk_props) | feet at (282,177) -> place(bg,spr,282,177) | all | Loose red plastic stool beside the sign post. Free to move. |
| shelter_front | 164x96 | 1 | (0,0) | shelter_front | (136,84) | all | Pillars x162-164 / x275-277 (feet y174), roof slab x160-279 y122-128 (top face 122-124, fascia 125-127, underside 128), header board "TRAM XE BUYT" x194-245 y130-142, blue bus-stop sign + route plate ("32") on post x287-288. |
| bougainvillea_xuan | 164x96 | 3 @3fps | (0,0) | bougainvillea | (136,84) | xuan | Green, scattered pink buds. |
| bougainvillea_ha | 164x96 | 3 @3fps | (0,0) | bougainvillea | (136,84) | ha | FULL bloom (hero), green peeking, fallen petals at planter. |
| bougainvillea_thu | 164x96 | 3 @3fps | (0,0) | bougainvillea | (136,84) | thu | Half bloom, gaps, faded/brown bracts, dry-green leaves. |
| bougainvillea_dong | 164x96 | 3 @3fps | (0,0) | bougainvillea | (136,84) | dong | Sparse dark leaves, few blooms, woody twigs visible. |
| decor_cau_doi_xuan | 164x96 | 1 | (0,0) | shelter_decor | (136,84) | xuan | Two couplets 6x30: left at scene (166,131), right (269,131) (inner faces of pillars). |
| decor_lanterns_xuan | 164x96 | 3 @3fps | (0,0) | shelter_decor | (136,84) | xuan | 4 red lanterns hanging from roof underside (y129) at x=177,188,253,267. Swing: body +-1, tassel +-1. |
| decor_lanterns_thu | 164x96 | 2 @2fps | (0,0) | shelter_decor | (136,84) | thu | Multi-colour paper-lantern strings along roof edge (x166-192, x247-273), 2-frame flicker. |
| decor_lights_dong | 164x96 | 3 @3fps | (0,0) | shelter_decor | (136,84) | dong | Fairy lights on roof edge + swags through the vine, 3-frame blink. |
| shelter_night_light | 164x96 | 1 | (0,0) | shelter_decor (above, night) | (136,84) | night | Emissive-only, no glow/dither: lit tube y131-132 x190-240, lit lightbox poster, lit header board. Compositor adds bloom. |
| shelter_wet | 164x96 | 1 | (0,0) | above shelter_front/seats | (136,84) | rain | Wet highlights on roof edge, seats, drips, puddle glints. |

## Previews
(rev2: ha has 3 longer drapes over the fascia at x~176-190 and ~250-258)
`_preview/shelter_composite_{xuan,ha,thu,dong}@3x.png` (+ `.gif` of sway), `shelter_composite_thu_night@3x.png`,
`shelter_composite_dong_night_wet@3x.png`. Composite z-order: shelter_back, seats, (waiting people), shelter_front,
bougainvillea, shelter_decor, wet / night glow.

## Compositor notes
* Sway frames: play 0,1,2 @3fps; core is static, only drapes/outer tips move +-1px.
* Decor pivots are baked into the canvas; no per-sprite anchors needed.
* Bougainvillea trunk/planter occupy x140-170 (left of shelter), canopy y~87-123, right spill to x~281, y~150.
* The glass bay of shelter_back is transparent (shows the building behind) with sparse reflection streaks.
