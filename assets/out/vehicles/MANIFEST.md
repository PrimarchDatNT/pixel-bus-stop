# vehicles MANIFEST

Strips of equally-sized frames; anchor = (x,y) at wheel contact (verified anchor y == frameH-1 for every wheel-anchored sprite). `_R` faces right (near lane, y=233, L->R), `_L` faces left (far lane, y=206, R->L). Layer: far_lane (`_L`) / near_lane (`_R`). No baked shadows.

| name | frame size | frames/fps | anchor | layer | suggested x/y | season | notes |
|---|---|---|---|---|---|---|---|
| bike_daisy_dong_L | 50x36 | 4/8 | (17, 35) | far_lane | y=206 | dong |  Bicycle flower vendor, nón lá; 4-frame pedal loop @8fps; cargo extends 15 px behind bike. Facing left. |
| bike_daisy_dong_R | 50x36 | 4/8 | (32, 35) | near_lane | y=233 | dong |  Bicycle flower vendor, nón lá; 4-frame pedal loop @8fps; cargo extends 15 px behind bike. Facing right. |
| bike_peach_xuan_L | 50x36 | 4/8 | (17, 35) | far_lane | y=206 | xuan |  Bicycle flower vendor, nón lá; 4-frame pedal loop @8fps; cargo extends 15 px behind bike. Facing left. |
| bike_peach_xuan_R | 50x36 | 4/8 | (32, 35) | near_lane | y=233 | xuan |  Bicycle flower vendor, nón lá; 4-frame pedal loop @8fps; cargo extends 15 px behind bike. Facing right. |
| bus_L | 170x52 | 4/12 | (85, 51) | far_lane | bus_L: place x=276 (front end at ~x=195) y=206 | all |  states {"drive": [0, 1], "stop": [2, 3]}. No doors (camera sees driver's side). Front-left end: raked windscreen with driver, LED sign above, headlights; rear: louvres + small window + taillights. stop = brake lights on + hazard blink (alternates each frame; use ~3fps). Frames 0-1 drive (wheel spin 12fps). Facing left. |
| bus_R | 170x52 | 6/12 | (85, 51) | near_lane | y=233 | all |  states {"drive": [0, 1], "doors_open": [2, 3], "stop": [4, 5]}. Frames 2-3 doors_open: 2=half, 3=full (play 2 then hold 3; reverse to close). Doors on this (right) side. Front door centre x=130, mid door centre x=80. stop = brake lights on + hazard blink (alternates each frame; use ~3fps). Frames 0-1 drive (wheel spin 12fps). Facing right. |
| bus_lights_L | 170x52 | 1/None | (85, 51) | overlay (same layer/pos as its vehicle) | same as vehicle | all |  Overlay, same frame size as bus_L: window glow (dithered), lit LED, head/tail lights |
| bus_lights_R | 170x52 | 1/None | (85, 51) | overlay (same layer/pos as its vehicle) | same as vehicle | all |  Overlay, same frame size as bus_R: window glow (dithered), lit LED, head/tail lights |
| car_lights_L | 72x24 | 1/None | (36, 23) | overlay (same layer/pos as its vehicle) | same as vehicle | all |  Overlay 72x24 for sedan_*/ (taxi: paste at y+7); head/tail lights dithered. |
| car_lights_R | 72x24 | 1/None | (36, 23) | overlay (same layer/pos as its vehicle) | same as vehicle | all |  Overlay 72x24 for sedan_*/ (taxi: paste at y+7); head/tail lights dithered. |
| cyclo_L | 64x34 | 4/8 | (32, 33) | far_lane | y=206 | all |  Xich lo: passenger carriage in front, driver pedalling behind; 4-frame pedal loop @8fps; facing L. |
| cyclo_R | 64x34 | 4/8 | (32, 33) | near_lane | y=233 | all |  Xich lo: passenger carriage in front, driver pedalling behind; 4-frame pedal loop @8fps; facing R. |
| moto_man_L | 32x28 | 2/12 | (15, 27) | far_lane | y=206 | all |  Facing left. 12fps wheel spin |
| moto_man_R | 32x28 | 2/12 | (16, 27) | near_lane | y=233 | all |  Facing right. 12fps wheel spin |
| moto_peach_L | 42x42 | 2/12 | (17, 41) | far_lane | y=206 | xuan, end of dong |  Facing left. 12fps wheel spin |
| moto_peach_R | 42x42 | 2/12 | (24, 41) | near_lane | y=233 | xuan, end of dong |  Facing right. 12fps wheel spin |
| moto_poncho_ha_L | 32x28 | 4/12 | (15, 27) | far_lane | y=206 | ha (rain) |  Facing left. 12fps wheel spin + poncho flutter (4 frames) |
| moto_poncho_ha_R | 32x28 | 4/12 | (16, 27) | near_lane | y=233 | ha (rain) |  Facing right. 12fps wheel spin + poncho flutter (4 frames) |
| moto_puffer_dong_L | 32x28 | 2/12 | (15, 27) | far_lane | y=206 | dong |  Facing left. 12fps wheel spin |
| moto_puffer_dong_R | 32x28 | 2/12 | (16, 27) | near_lane | y=233 | dong |  Facing right. 12fps wheel spin |
| moto_quat_xuan_L | 44x32 | 2/12 | (15, 31) | far_lane | y=206 | xuan |  Facing left. 12fps wheel spin |
| moto_quat_xuan_R | 44x32 | 2/12 | (28, 31) | near_lane | y=233 | xuan |  Facing right. 12fps wheel spin |
| moto_sun_ha_L | 32x28 | 2/12 | (15, 27) | far_lane | y=206 | ha (xuan/thu ok) |  Facing left. 12fps wheel spin |
| moto_sun_ha_R | 32x28 | 2/12 | (16, 27) | near_lane | y=233 | ha (xuan/thu ok) |  Facing right. 12fps wheel spin |
| scooter_couple_L | 38x28 | 2/12 | (15, 27) | far_lane | y=206 | all |  Facing left. 12fps wheel spin |
| scooter_couple_R | 38x28 | 2/12 | (22, 27) | near_lane | y=233 | all |  Facing right. 12fps wheel spin |
| sedan_red_L | 72x24 | 2/12 | (36, 23) | far_lane | y=206 | all |  Sedan, facing left, 2 wheel frames @12fps. |
| sedan_red_R | 72x24 | 2/12 | (36, 23) | near_lane | y=233 | all |  Sedan, facing right, 2 wheel frames @12fps. |
| sedan_silver_L | 72x24 | 2/12 | (36, 23) | far_lane | y=206 | all |  Sedan, facing left, 2 wheel frames @12fps. |
| sedan_silver_R | 72x24 | 2/12 | (36, 23) | near_lane | y=233 | all |  Sedan, facing right, 2 wheel frames @12fps. |
| sedan_white_L | 72x24 | 2/12 | (36, 23) | far_lane | y=206 | all |  Sedan, facing left, 2 wheel frames @12fps. |
| sedan_white_R | 72x24 | 2/12 | (36, 23) | near_lane | y=233 | all |  Sedan, facing right, 2 wheel frames @12fps. |
| taxi_L | 72x31 | 2/12 | (36, 30) | far_lane | y=206 | all |  Sedan, facing left, 2 wheel frames @12fps; 72x31 incl. roof sign. |
| taxi_R | 72x31 | 2/12 | (36, 30) | near_lane | y=233 | all |  Sedan, facing right, 2 wheel frames @12fps; 72x31 incl. roof sign. |
| van_L | 76x32 | 2/12 | (38, 31) | far_lane | y=206 | all |  Delivery box van, facing L; 2 wheel frames @12fps. Light is upper-left only on R; L is a flip. |
| van_R | 76x32 | 2/12 | (38, 31) | near_lane | y=233 | all |  Delivery box van, facing R; 2 wheel frames @12fps. Light is upper-left only on R; L is a flip. |
| van_quat_xuan_L | 76x32 | 2/12 | (38, 31) | far_lane | y=206 | xuan |  Open-bed truck loaded with 3 kumquat trees (Tet); facing L. |
| van_quat_xuan_R | 76x32 | 2/12 | (38, 31) | near_lane | y=233 | xuan |  Open-bed truck loaded with 3 kumquat trees (Tet); facing R. |

## Notes
- bus_L (far lane) shows the driver's side: no doors; states drive / stop (brake + hazards, alternate frames ~3fps). bus_R (near lane) shows the door side: drive / doors_open / stop.
- taxi frames are 72x31 (roof sign headroom); car_lights overlay is 72x24: paste at y+7 for taxi.
- Overlays carry dithered glows only; the compositor should add light cones.
- _L of cars/motos/bikes/vans are flips (light from upper right); bus is re-lit.
- Placement check: _preview/placement_check@3x.png