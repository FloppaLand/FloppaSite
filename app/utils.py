import os
from app import app
from werkzeug.utils import safe_join
from PIL import Image

def get_skin_patch(filename):
   filename = filename + ("" if filename.lower().endswith(".png") else ".png")# проверка на .png
   if os.path.exists(safe_join(app.config['UPLOADED_SKINS_DIR'], filename)):
    return [app.config['UPLOADED_SKINS_DIR'], filename]
   else:
      return [app.config['UPLOADED_SKINS_DIR'], "base.png"]

def resize_bg(image_pil, width, height):
    background = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    offset = (round( (width - image_pil.width) / 2), round((height - image_pil.height) / 2))
    background.paste(image_pil, offset)
    return background