from _common import *
import tools.px as _px
place={
 'woman_wait':('(150, 179)  [x anywhere on seat x 130-225; y = SEAT_Y-1]','seated, faces left; legs dangle ~7px above ground (seat is 16px high). z: above shelter seat, behind shelter glass/posts'),
 'shopkeeper':('(285, 185)  [gap in H3 grocery, x 280-290; y = counter-top line, waist hidden by counter]','z: behind counter/shop window glare, in front of shop shelves'),
 'tea_stall':('(278, 196)  [sprite spans x 262-294]','z: in front of sidewalk, behind stools/old man? (old man in front of table edge)'),
 'stool_red':('(299, 196), (322, 196)','z: above sidewalk; empty stools'),
 'stool_blue':('(311, 196)','z: below oldman_tea thigh'),
 'oldman_tea':('(303, 196)  [sits on stool_blue at 311, faces the table]','z: above stool_blue'),
 'steam':('(269, 172)  [above thermos cap; y = thermos top]','z: top-most of the stall; use 70% opacity in compositor'),
 'cat_sleep':('(214, 145)  [CAT_SPOT x, roof top y-1]','z: on top of shelter roof / in front of bloom'),
 'cat_tail':('(214, 145)  same place; swap with cat_sleep for a tail-flick moment','tail hangs over roof edge; same body pixels as cat_sleep frame 0'),
 'cat_sit':('(214, 145) alternative pose','11px tall, faces left'),
 'sparrow_perch':('perches: (132, 91) H1 parapet top (x 124-190, roof y~58: use y=58 if H1 roof), (214, 22) H2 roof top; (300, 80) H3 parapet; also shelter roof edge (230,146)','suggest y = roof_top_y - 0; faces left, flip for right'),
 'sparrow_fly':('path e.g. (140,70) -> (230,50), x -3px/frame at 4 fps wing; loop 8 fps','flip for direction; draw above everything except foliage'),
 'moto_parked':('(353, 196)  [MOTORBIKE_X+17 = sprite centre; front wheel right]','z: on sidewalk, in front of H4 facade'),
 'walker_nonla':('walk along sidewalk y=196, e.g. x from -20 to 404 at ~12 px/s; flip for left','z: in front of shelter?/behind trà đá; loop 6 frames'),
 'scooter_rider':('(x, 213)  road lane, y = WHEEL_Y; flip for left lane','z: above road, in front of curb'),
}
L=['# actors MANIFEST','',
 'Anchor convention: `anchor` = pixel inside the frame; paste the frame at (X-ax, Y-ay) so that anchor lands on canvas (X, Y).',
 'Anchor y is the lowest pixel row of the contact (feet / wheels / roof) - except woman_wait, whose anchor is the thigh-bottom row that touches the seat. All sprites have transparent bg, 1px selective outline, palette-validated.',
 'Light is from the upper-left; no baked shadows (compositor adds them). Sprites face LEFT unless noted (flip as needed).','',
 '| sprite | size | frames | fps | anchor (in frame) | canvas placement (X, Y of anchor) | z / notes |','|---|---|---|---|---|---|---|']
import json
for n,(p,z) in place.items():
    m=json.load(open(_px.OUT/'actors'/f'{n}.json'))
    L.append(f"| {n} | {m['frameW']}x{m['frameH']} | {m['frames']} | {m['fps'] or '-'} | {tuple(m['anchor'])} | {p} | {z} |")
L+=['','Facing: moto_parked, walker_nonla, scooter_rider face RIGHT; woman_wait, oldman_tea, cats, sparrows face LEFT; shopkeeper is front view.',
 '','Stall layout (x): table sprite 262-294, stool_red 299, oldman on stool_blue 303/311, stool_red 322. Steam over the thermos (thermos is at table sprite x+1..+9).',
 '','Known compromises: woman_wait legs dangle (seat 16px high, no footrest); sparrows are 8-9px blobs; scooter face is mostly helmet+mask by design.']
(_px.OUT/'actors'/'MANIFEST.md').write_text('\n'.join(L)+'\n')
