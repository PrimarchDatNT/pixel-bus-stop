from bloom import *
im, m, d = bloom_layer()
im.save("/tmp/bl0.png")
back = Image.open(ROOT/"assets/out_gif/_mock/mock3.png").convert("RGBA")
back.alpha_composite(im)
back.crop((0,30,210,200)).resize((210*4,170*4),0).save("/tmp/bl_prev.png")
