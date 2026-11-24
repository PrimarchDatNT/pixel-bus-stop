from view import *
DECOR = {"xuan": ["decor_cau_doi_xuan", "decor_lanterns_xuan"], "ha": [], "thu": ["decor_lanterns_thu"], "dong": ["decor_lights_dong"]}

def full(season, f=0, extra=(), wet=False, night=False):
    bg = mock_scene()
    if night:
        bg.alpha_composite(Image.new("RGBA", bg.size, (*RGB["navy"], 255)).point(lambda v: v) , (0,0)) if False else None
    for n in ["shelter_back", "seats"]:
        bg.alpha_composite(ld(n), (OX, OY))
    rect(bg, 236, WAIT_BASE_Y - ADULT_H + 1, 240, WAIT_BASE_Y, "ink")
    bg.alpha_composite(ld("shelter_front"), (OX, OY))
    st = ld("stool_red"); bg.alpha_composite(st, (282 - st.width // 2, 177 - st.height + 1))
    bg.alpha_composite(ld("bougainvillea_" + season, f), (OX, OY))
    for d in DECOR[season] + list(extra):
        bg.alpha_composite(ld(d, f % ld_frames(d)), (OX, OY))
    if wet: bg.alpha_composite(ld("shelter_wet"), (OX, OY))
    return bg

def ld_frames(n):
    return json.loads((OUT/GROUP/f"{n}.json").read_text())["frames"]

if __name__ == "__main__":
    for s in SEASONS_:
        bg = full(s)
        save_mock(bg, GROUP, f"shelter_composite_{s}")
    # extras
    save_mock(full("thu", extra=["shelter_night_light"]), GROUP, "shelter_composite_thu_night")
    save_mock(full("dong", extra=["shelter_night_light"], wet=True), GROUP, "shelter_composite_dong_night_wet")
    # gifs of sway
    S_ = OUT/GROUP/"_preview"
    for s in SEASONS_:
        fr = [full(s, f).crop((130,84,310,184)).resize((180*4,100*4), Image.NEAREST).convert("RGB") for f in range(3)]
        fr[0].save(S_/f"shelter_composite_{s}.gif", save_all=True, append_images=fr[1:], duration=333, loop=0)
