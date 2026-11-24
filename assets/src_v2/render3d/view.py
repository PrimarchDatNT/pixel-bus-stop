import sys
from PIL import Image
src, dst, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
box = tuple(map(int, sys.argv[4:8])) if len(sys.argv) > 4 else None
im = Image.open(src).convert('RGBA')
bg = Image.new('RGBA', im.size, (255, 0, 255, 255)); bg.alpha_composite(im)
if box: bg = bg.crop(box)
bg.resize((bg.width * k, bg.height * k), Image.NEAREST).convert('RGB').save(dst)
