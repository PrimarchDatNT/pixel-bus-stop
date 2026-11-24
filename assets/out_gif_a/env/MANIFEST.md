# env group (scenery, full-canvas 384x216, anchor (0,0), place at canvas (0,0))

Scripts: `assets/src_gif/env/` (`sky_ground.py`, `houses.py`, `tree.py`, helpers `common.py`, `parts.py`; `comp.py` = preview compositor).

| z (low->high) | layer | frames / fps | notes |
|---|---|---|---|
| 0 | `sky` | 1 | 3 flat bands (sky_m 0-5, sky 6-95, sky_hl 96-185), 3 flat-shaded clouds over H1 (~x128-176,y22-40), H3 (~x258-306,y42-62), H4 (~x333-360,y16-28). Covers y 0-185 only |
| 1 | `skyline` | 1 | haze_* tube-house silhouettes, rooftop tanks/antennas, far tree line; no outlines. Covers y 62-185 |
| 2 | `ground` | 1 | sidewalk 186-199 (pave tiles, lit top edge y186), curb 200-202, road 203-215 with dashed lane line y=209. Tree trunk base and props overlap it, so draw tree/shelter/actors above |
| 3 | `houses` (= house_0..house_4 merged) | 1 | five nha ong, facades end at y=185 |
| 3 | `house_0` .. `house_4` | 1 | same content, one per house (each clipped to its HOUSES x-range) |
| 6 | `tree` | 3 @ 3 fps | street tree, trunk x=34, canopy ~(0,0)-(110,118), whitewashed trunk base at y 176-196. Only edge clumps move 1 px, trunk is static. Put it above shelter/houses (canopy overhangs H0), below nothing else |

Suggested stack: sky, skyline, ground, houses, [shelter], tree, actors. The tree overlaps H0 and the bougainvillea
zone x 86-110: decide in the compositor whether the shelter bloom goes over or under the canopy.

## Houses
- H0 pale blue: blue shutters, roller shutter + door "12", roof antennas. Mostly under the tree.
- H1 ochre: 2 balconies (bougainvillea target = 1st upper floor, y ~107-150), green/blue shutters, roof tank + antenna; ground = cafe, signboard `CÀ PHÊ` (x 134-176, y 152-163), counter + lamps behind (mostly hidden by shelter).
- H2 pink, tallest: 4 balconies with plants, laundry line on floor 2 (y ~ 96-108), roof tank + antenna; ground = rolling shutter + green door.
- H3 cream: ground floor is 46 px tall (y 140-185), `TẠP HÓA` sign, striped awning, shelves with goods, counter at y 180-185, one air-conditioner on the 1st upper floor (x ~298-311, y ~ 97).
- H4 ochre: 3 balconies + hanging plants, roof tank + antenna; ground = `PHỞ BÒ` red sign with lanterns, rolled-up shutter box, stainless pot and counter.

## Shopkeeper gap (H3 tap hoa)
Flat mid-brown back wall, nothing drawn in it: **x 276-285, y 160-179** (10x20). Counter top edge is at y=180 (counter front y 180-185),
so a seated shopkeeper's feet/stool can sit at about y 186 behind the counter; suggested actor anchor (feet) = (281, 186)
or, if seated at the counter, centre-bottom at (281, 179). Back wall around it: x 273-288, y 158-179. Awning bottom at y 158.
