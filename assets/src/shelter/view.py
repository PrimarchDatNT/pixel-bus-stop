import sys
from common import *
from PIL import Image
import json
S="/private/tmp/claude-501/-Users-datnt1-Desktop-work-local-llm/aecac36a-4fde-49ae-bc08-0eb2ae68421d/scratchpad/"
def ld(name, f=0):
    im = Image.open(OUT/GROUP/f"{name}.png").convert("RGBA")
    m = json.loads((OUT/GROUP/f"{name}.json").read_text()); w=m["frameW"]
    return im.crop((f*w,0,(f+1)*w,im.height))
def scene(season, f=0, decor=True):
    bg = mock_scene()
    # hide mock shelter: repaint bg region
    for n in ["shelter_back","seats"]:
        bg.alpha_composite(ld(n),(OX,OY))
    rect(bg,236,WAIT_BASE_Y-ADULT_H+1,240,WAIT_BASE_Y,"ink")
    bg.alpha_composite(ld("shelter_front"),(OX,OY))
    bg.alpha_composite(ld("stool_red"),(282-5,177-11))
    bg.alpha_composite(ld("bougainvillea_"+season,f%3),(OX,OY))
    return bg
if __name__=="__main__":
    s=sys.argv[1]; k=int(sys.argv[2]) if len(sys.argv)>2 else 6
    bg=scene(s)
    bg.crop((130,84,310,184)).resize((180*k,100*k),Image.NEAREST).save(S+f"c_{s}.png")
