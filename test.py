from PIL import Image

img = Image.open('./ZizazrSteampunk.png')
box = (8, 8, 16, 16)
img = img.crop(box)
img.show()