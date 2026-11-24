import sys
from PIL import Image
names, out = sys.argv[2:], sys.argv[1]
ims=[Image.open(n) for n in names]
w,h=ims[0].size
o=Image.new('RGB',(w*2,h*((len(ims)+1)//2)))
for i,im in enumerate(ims): o.paste(im,((i%2)*w,(i//2)*h))
o.save(out)
