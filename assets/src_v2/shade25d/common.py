import sys, os
ROOT = '/Users/datnt1/Desktop/work/local-llm/pixel-bus-stop'
sys.path.insert(0, ROOT + '/tools')
from shade25d import *
OUT = ROOT + '/assets/out_v2/shade25d/'
os.makedirs(OUT, exist_ok=True)
SCR = '/private/tmp/claude-501/-Users-datnt1-Desktop-work-local-llm/aecac36a-4fde-49ae-bc08-0eb2ae68421d/scratchpad/'

def crop_img(img, box):
    return img.crop(box)

def zoom(img, k=6, bg=(110,170,225,255), box=None, name='z.png'):
    if box: img = img.crop(box)
    bgi = Image.new('RGBA', img.size, bg); bgi.alpha_composite(img)
    bgi.resize((bgi.width*k, bgi.height*k), Image.NEAREST).save(SCR+name)
