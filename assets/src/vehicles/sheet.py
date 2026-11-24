import sys
from PIL import Image
S="/private/tmp/claude-501/-Users-datnt1-Desktop-work-local-llm/aecac36a-4fde-49ae-bc08-0eb2ae68421d/scratchpad/"
names=sys.argv[2:]; ims=[]
for k in names:
    i=Image.open(f"assets/out/vehicles/_preview/{k}@4x.png"); ims.append(i)
W=max(i.width for i in ims);H=sum(i.height for i in ims)
o=Image.new("RGB",(W,H),(192,203,220));y=0
for i in ims:o.paste(i,(0,y));y+=i.height
o.save(S+sys.argv[1]+".png");print(o.size)
