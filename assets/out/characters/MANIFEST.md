# characters MANIFEST

All sprites face RIGHT in `_R`; `_L` is a flip (anchor mirrored). Default anchor bottom-centre = feet. Walk cycles move feet 2px/frame in stance: scroll 2px/frame (16px/s @8fps; elder fps 6 -> 12px/s; run ~3.5px/frame; dog and cat walk 2px/frame) to avoid foot sliding.
Sitting people: seat surface ~7px above the feet row; anchor x = hip/seat centre.
Cat coats: `cat` (orange tabby), `cat_black`, `cat_calico`, `cat_tuxedo`, `cat_grey` share identical frames/states/state_fps/anchor (24,29). States in each JSON (`states`, `state_fps`, `state_loop`): walk 0-7, sit_down 8-10, sit_idle 11-14, lick_paw 15-20 (raised paw now outlined with pink pad), look_camera 21-22, lie_down 23-25, sleep 26-29 (curled ball). Calico patches are painted by body region (head, back saddle, rump, tail tip), consistent across frames.
Sparrow states: fly 0-3, idle 4-5, peck 6-7, hop 8-9.
Watchers (watch_*): fireworks night; watch_shoulders_dong is ~40px tall; watch_couple_dong is 40px wide.

| name | frame | frames/fps | anchor | layer | suggested x/y | season | notes |
|---|---|---|---|---|---|---|---|
| cat_R / _L | 48x30 | 30f @ 10fps | (24, 29) | foreground_actors | y=264 (CAT_BASE_Y), x~360 | all | foreground cat (orange coat), 1.6x. states walk(8@10, 2px/frame), sit_down(3@6 one-shot), sit_idle(4@4), lick_ |
| cat_black_R / _L | 48x30 | 30f @ 10fps | (24, 29) | foreground_actors | y=264 (CAT_BASE_Y), x~360 | all | foreground cat (black coat), 1.6x. states walk(8@10, 2px/frame), sit_down(3@6 one-shot), sit_idle(4@4), lick_p |
| cat_calico_R / _L | 48x30 | 30f @ 10fps | (24, 29) | foreground_actors | y=264 (CAT_BASE_Y), x~360 | all | foreground cat (calico coat), 1.6x. states walk(8@10, 2px/frame), sit_down(3@6 one-shot), sit_idle(4@4), lick_ |
| cat_grey_R / _L | 48x30 | 30f @ 10fps | (24, 29) | foreground_actors | y=264 (CAT_BASE_Y), x~360 | all | foreground cat (grey coat), 1.6x. states walk(8@10, 2px/frame), sit_down(3@6 one-shot), sit_idle(4@4), lick_pa |
| cat_tuxedo_R / _L | 48x30 | 30f @ 10fps | (24, 29) | foreground_actors | y=264 (CAT_BASE_Y), x~360 | all | foreground cat (tuxedo coat), 1.6x. states walk(8@10, 2px/frame), sit_down(3@6 one-shot), sit_idle(4@4), lick_ |
| dog_R / _L | 32x18 | 6f @ 10fps | (16, 17) | far_walkers | y=178, 2px/frame | all | street dog trot 6f; ground speed 2px/frame (20px/s @10fps) |
| run_rain_ha_R / _L | 36x35 | 6f @ 12fps | (18, 34) | far_walkers | y=178, ~3.5px/frame into shelter | ha | running, bag held over head; ~3.5px/frame ground speed (~42px/s @12fps) |
| sit_elder_R / _L | 32x29 | 3f @ 3fps | (14, 28) | waiting_people | y=172 (WAIT_BASE_Y), x 165..270 | all | waiting person; feet at WAIT_BASE_Y; sit_* anchor x = hip/seat centre (seat surface ~7px above feet row) |
| sit_phone_dong_R / _L | 32x29 | 3f @ 3fps | (14, 28) | waiting_people | y=172 (WAIT_BASE_Y), x 165..270 | dong | waiting person; feet at WAIT_BASE_Y; sit_* anchor x = hip/seat centre (seat surface ~7px above feet row) |
| sit_phone_ha_R / _L | 32x29 | 3f @ 3fps | (14, 28) | waiting_people | y=172 (WAIT_BASE_Y), x 165..270 | ha | waiting person; feet at WAIT_BASE_Y; sit_* anchor x = hip/seat centre (seat surface ~7px above feet row) |
| sparrow_R / _L | 9x7 | 10f @ 10fps | (4, 6) | far_walkers/sky | sky y 20-100; sparrow perch on wires | all | chim se; states: fly 4f@10fps, idle 2f@2fps, peck 2f@4fps, hop 2f@4fps (perched states anchor = feet) |
| stand_wait_dong_R / _L | 32x29 | 4f @ 2fps | (16, 28) | waiting_people | y=172 (WAIT_BASE_Y), x 165..270 | dong | waiting person; feet at WAIT_BASE_Y; sit_* anchor x = hip/seat centre (seat surface ~7px above feet row) |
| stand_wait_ha_R / _L | 32x29 | 4f @ 2fps | (16, 28) | waiting_people | y=172 (WAIT_BASE_Y), x 165..270 | ha | waiting person; feet at WAIT_BASE_Y; sit_* anchor x = hip/seat centre (seat surface ~7px above feet row) |
| swallow_R / _L | 9x7 | 4f @ 10fps | (4, 3) | far_walkers/sky | sky y 20-100; sparrow perch on wires | all | chim en, 9x7, anchor = body centre (flying: not ground-based) |
| walk_aodai_xuan_R / _L | 32x29 | 6f @ 8fps | (16, 28) | far_walkers | y=178 (WALK_FAR_BASE_Y) | xuan | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_cardigan_thu_R / _L | 32x29 | 6f @ 8fps | (16, 28) | far_walkers | y=178 (WALK_FAR_BASE_Y) | thu | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_coat_dong_R / _L | 32x29 | 6f @ 8fps | (16, 28) | far_walkers | y=178 (WALK_FAR_BASE_Y) | dong | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_elder_xuan_R / _L | 32x29 | 6f @ 6fps | (16, 28) | far_walkers | y=178 (WALK_FAR_BASE_Y) | xuan | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_kid_thu_R / _L | 24x21 | 6f @ 8fps | (12, 20) | far_walkers | y=178 (WALK_FAR_BASE_Y) | thu | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_kid_xuan_R / _L | 24x21 | 6f @ 8fps | (12, 20) | far_walkers | y=178 (WALK_FAR_BASE_Y) | xuan | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_man_xuan_R / _L | 32x29 | 6f @ 8fps | (16, 28) | far_walkers | y=178 (WALK_FAR_BASE_Y) | xuan | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_puffer_dong_R / _L | 32x29 | 6f @ 8fps | (16, 28) | far_walkers | y=178 (WALK_FAR_BASE_Y) | dong | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_schoolgirl_ha_R / _L | 32x29 | 6f @ 8fps | (16, 28) | far_walkers | y=178 (WALK_FAR_BASE_Y) | ha | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_tshirt_ha_R / _L | 32x29 | 6f @ 8fps | (16, 28) | far_walkers | y=178 (WALK_FAR_BASE_Y) | ha | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| walk_umbrella_ha_R / _L | 40x37 | 6f @ 8fps | (20, 36) | far_walkers | y=178 (WALK_FAR_BASE_Y) | ha | walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps |
| watch_couple_dong_R / _L | 40x31 | 2f @ 3fps | (20, 30) | far_walkers / waiting_people | fireworks night, y=178 or 172, feet anchor | dong | fireworks night watcher, face tilted up; anchor bottom-centre (feet) |
| watch_phone_dong_R / _L | 32x33 | 2f @ 2fps | (16, 32) | far_walkers / waiting_people | fireworks night, y=178 or 172, feet anchor | dong | fireworks night watcher, face tilted up; anchor bottom-centre (feet) |
| watch_point_dong_R / _L | 32x35 | 3f @ 3fps | (16, 34) | far_walkers / waiting_people | fireworks night, y=178 or 172, feet anchor | dong | fireworks night watcher, face tilted up; anchor bottom-centre (feet) |
| watch_shoulders_dong_R / _L | 32x47 | 3f @ 3fps | (16, 46) | far_walkers / waiting_people | fireworks night, y=178 or 172, feet anchor | dong | fireworks night watcher, face tilted up; anchor bottom-centre (feet) |
