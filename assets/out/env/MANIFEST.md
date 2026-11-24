# env — MANIFEST
Scripts: assets/src/env/{ground,buildings,pole_wires,lamp,tree,clouds,decor,composite}.py. All frames palette-validated. Previews in `_preview/` (see `env_composite@3x.png`, `env_composite_night@3x.png`).

| name | frame size | frames/fps | anchor | layer (Z_ORDER) | place at (top-left unless noted) | season | notes |
|---|---|---|---|---|---|---|---|
| ground | 480x112 | 1 | top-left | ground | (0,158) | all | opaque; local y = scene y-158; bands exactly per layout.py |
| ground_wet | 480x112 | 1 | top-left | ground (overlay) | (0,158) | rain/after rain | puddles w/ sky reflections + dark sheen dashes |
| buildings | 480x130 | 1 | top-left | buildings | (0,32) | all | 8 tube houses; bottom row = scene y161; ground floors visible down to y157 |
| buildings_lights | 480x130 | 1 | top-left | buildings_lights | (0,32) | night | solid lit windows (curtain/lamp/silhouette), solid warm shop interiors with silhouettes, brighter solid signs; no dithers/halos |
| buildings_decor_xuan | 480x130 | 1 | top-left | buildings_lights (above) | (0,32) | xuan | VN flags on balconies, red lanterns by signs |
| buildings_decor_thu | 480x130 | 1 | top-left | buildings_lights (above) | (0,32) | thu | lantern strings over shop fronts, star lanterns on balconies |
| pole_wires | 480x170 | 1 | top-left | wires_pole | (0,0) | all | pole centre x=52, base y=165; wires y35-80 |
| lamp | 36x82 | 1 | (4,78) pole foot | lamp | (288,90) -> base lands (296,170) | all | head y~96-101, arm to the right |
| lamp_lit | 36x82 | 1 | (4,78) | above lamp | (288,90), same as lamp | night | emissive lens row only (no baked glow). Bulb centre = scene (310,98) |
| tree_trunk | 130x137 | 1 | (68,136) trunk foot | tree_trunk | (350,30) -> base (418,166) | all | 5 tiers; twigs bare |
| tree_canopy_xuan | 130x95 | 1 | top-left | tree_canopy | (350,30) | xuan | sparse fresh green |
| tree_canopy_ha | 130x95 | 2 @2fps | top-left | tree_canopy | (350,30) | ha | lush; 1px sway; flat pagoda pads per tier |
| tree_canopy_thu | 130x95 | 2 @2fps | top-left | tree_canopy | (350,30) | thu | yellow/orange/gold + few green |
| tree_canopy_dong | 130x95 | 1 | top-left | tree_canopy | (350,30) | dong | few red/rust leaves |
| cloud_l1 / cloud_l2 | 120x48 / 94x38 | 1 | top-left | clouds | sky y 4-60 | xuan/ha/thu | flat-bottom fair-weather |
| cloud_s1 / cloud_s2 | 52x22 / 40x18 | 1 | top-left | clouds | sky | | |
| cloud_rain1 / cloud_rain2 | 230x62 / 190x54 | 1 | top-left | clouds | sky y 0-50 | ha storm (dong overcast) | slate ramp, tattered underside |

## Bird perch points on wires (scene px, feet position)
(88,38) (140,45) (220,52) (250,54) (310,54) (360,52) (400,49) (440,45)

## Notes
* Rev 2: phone number replaced by "SỬA KHÓA" on GIẶT LÀ shutter; lamp_glow removed; ground sidewalks calmed (mortar grey, close values); canopies rebuilt as flat tiered pads.
* Z-order caveat: pole/lamp/tree_trunk feet sit at y165-170, below ground top (158). The compositor must draw `ground` BEFORE wires_pole/tree_trunk/lamp (or Z_ORDER in layout.py is wrong); my env_composite does so.
* Shop/sign texts: TẠP HÓA, PHỞ BÒ, CẮT TÓC, SỬA XE, CÀ PHÊ, BÁNH MÌ, ĐIỆN MÁY, GIẶT LÀ. Shelter (x160-279) hides most of SỬA XE / CÀ PHÊ ground floors.
