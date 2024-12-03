import os
from app import app
from werkzeug.utils import safe_join
from PIL import Image
from minepi import Skin
import asyncio
from hashlib import sha256
import json
def get_skin_patch(filename):
   filename = filename + ("" if filename.lower().endswith(".png") else ".png") # проверка на .png
   
   if os.path.exists(safe_join(app.config['UPLOADED_SKINS_DIR'], filename)):
    return [app.config['UPLOADED_SKINS_DIR'], filename]
   else:
      return [app.config['UPLOADED_SKINS_DIR'], "base.png"]

def resize_bg(image_pil, width, height):
    background = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    offset = (round( (width - image_pil.width) / 2), round((height - image_pil.height) / 2))
    background.paste(image_pil, offset)
    return background

def render_body(skin_path, render_cache):
   raw_skin = Image.open(skin_path)
   s = Skin(raw_skin=raw_skin)
   renders=[]

   for i in range(1, 360, 5):
      asyncio.run(s.render_skin(vr=-30, hr=i))
      renders.append(resize_bg(s.skin, 200, 400))

   renders[0].save(safe_join(app.config['BODY_RENDERS_DIR'], render_cache +'.gif'), 'GIF', save_all=True, append_images=renders[1:], duration=80, loop=0, disposal=2)
   

def validate_data_file(filename):
   path = os.path.join(app.config['DATA_DIR'], filename)

   if os.path.exists(path):  
      return True
   else:
      with open(path, 'w', encoding='utf-8') as f:
         f.write('[]')
      return False

def calculate_file_hash(file_path):
    with open(file_path, "rb") as f:
      file_hash = sha256(f.read()).hexdigest()
    return file_hash

def update_hash(caches, username, skin_hash):
   caches[username] = skin_hash
   
   with open(os.path.join(app.config['DATA_DIR'], 'render-cache.json'), 'w', encoding='utf-8') as f:
      json.dump(caches, f)
   return caches[username]