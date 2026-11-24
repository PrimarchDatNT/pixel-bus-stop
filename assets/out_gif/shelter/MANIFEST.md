# shelter group, composition B (scripts: assets/src_gif/shelter_b/*.py)

All layers are full-canvas 384x216, anchor (0,0), placed at (0,0).
Z-order (back to front): `shelter_back` < `seats` < [seated woman at WAITER_SPOT] < `shelter_front` < `bougainvillea` < `stop_sign`
(the cat sits on the roof at CAT_SPOT, above `shelter_front`; the bloom leaves x146-170 clear below y~137 for it).

| layer | frames/fps | notes |
|---|---|---|
| shelter_back | 1 | Glass rear wall x41-170 y154-195 (transparent panes, light rails, glare), kick panel y191-195, muted lightbox "CAFE" x50-70, route map "32" x73-86 (y159-180). |
| seats | 1 | 4 blue moulded modules x44-76, 80-112 (free seat, WAITER_SPOT x96), 116-148, 152-169; seat top y188, legs to y196. |
| shelter_front | 1 | Pillars x37-39 / x171-173, roof slab x36-176 y150-154 (lit top, shade under), header board "TRẠM XE BUÝT" x110-169 y157-172 (clear of x86-106). |
| bougainvillea | 3 @ 3fps | HERO. Planter x22-36 y184-196, twisting trunk with fork and branches seen through gaps in the crown (x6-65, y98-185); bloom mass x4-200 y36-152 (tall left crown, pour over the roof, climbing part x148-200 over the house's left side), leaf clusters, ~20 drapes, loose bracts. Trunk/planter/core static; outer pixels and drapes sway 1 px. |
| stop_sign | 1 | Post at STOP_SIGN_X 312, blue bus plate x306-319 y128-141, route plate "32" y143-152. |
| petals | 4 @ 6fps | 3x3 tumbling bract, anchor (1,1) centre; spawn near drape edges x4-200 y120-160, fall to y196. |

Preview: `_preview/shelter_composite@4x.png`.
