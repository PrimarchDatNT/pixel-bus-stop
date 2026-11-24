# env (composition B)
All layers: 384x216, 1 frame, anchor (0,0). Source: assets/src_gif/env_b/ (run.py builds everything).

| z | layer | notes |
|---|-------|-------|
| 0 | sky.png | 3 flat bands (sky_m / sky / sky_hl horizon); clouds: big upper right (x~300-365,y~22-44), small at (~105-130,y~12-20), (~258-282,y~8-14), (~38-56,y~21-27) |
| 1 | distance.png | haze colours, no outlines: skyline + water tanks (x296-384), Long Bien truss bridge (deck y160-161, piers x320/362), river y163-172, far street band y172-186 across full width |
| 2 | house.png | hero shophouse x142-309 (roof overhang), tiled roof ridge y46, dormer (206,30,230,48), stainless tank on ridge, balcony slab y120-123, railing y110-119, shop opening y128-185 |
| 3 | ground.png | sidewalk y186-199 (tile pattern, lit top edge), curb y200-202, road y203-215 with dashed lane at y209-210 |

Key positions in house.png
- Counter top edge: **y = 176** (x156-293), display case below it.
- Shopkeeper spot (236,176): clear 14x20 at x229-243, y156-175 (warm alcove with blue valance behind, bulb at 236,153).
- Grandma spot (262,120): clear x257-267, y92-119 (open French door with dim interior, shutters open).
- Birdcage hook (196,98): bracket + chain end at y97, wall gap x192-201 kept free.
- Signs: TAP HOA board (x200-268,y126-149), CHE board (179-191,y129-140), CA PHE board (271-294), red lantern x194-198.
- Shelves/fridge are in x157-293; left of x178 is hidden by the shelter.
- Bougainvillea should overlap the house's left side (x<~195); windows/shutters there are fully drawn underneath.

Preview: _preview/env_composite@3x.png (env over mock3 pink/shelter shapes).
