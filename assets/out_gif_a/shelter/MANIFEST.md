# shelter group (scripts: assets/src_gif/shelter/*.py)

All layers are full-canvas 384x216, anchor (0,0), placed at (0,0).

Z-order (back to front): `shelter_back` < `seats` < [seated person] < `shelter_front` < `bougainvillea` < `stop_sign`

| layer | frames/fps | notes |
|---|---|---|
| shelter_back | 1 | Rear wall x118-231, y151-196. Transparent glass panes; lit "CÀ PHÊ" lightbox LEFT x122-146 y156-187; route map RIGHT x206-228 y165-187 (below the header board).
| seats | 1 | Blue moulded bench x150-203, seat top y188 (SEAT_Y), legs to y196. Module 1 (x150-182) is for the seated adult around x160-180. |
| shelter_front | 1 | Pillars x116-118 / x230-232, roof slab x112-236 y146-150 (lit top, shade below), header board "TRẠM XE BUÝT" x182-229 y152-165 (all diacritics visible). Clear of x<182, so a head at x165-181 is not covered.
| bougainvillea | 3 @ 3fps | Planter x100-112 y184-196, trunk up the left pillar, bloom mass x88-250 y98-160 with drapes. Trunk, planter and core clumps are static; edge clumps and drapes sway 1 px. Roof right of x207 up to x224 is left clear for the cat at (214,146). |
| stop_sign | 1 | Post x244-245, blue plate x238-251 y128-141, route plate "32" y143-152. |
| petals | 4 @ 6fps | 3x3 actor-style sprite, anchor (1,1) centre. Compositor spawns many near drape edges (e.g. x90-250, y120-160) falling to y196. |

Preview: `_preview/shelter_composite@4x.png` (over the blocking mock).
