from flask import render_template, flash, redirect, url_for, request, send_file, send_from_directory, make_response
from app.utils import calculate_file_hash, get_skin_patch, render_body, update_hash
from werkzeug.utils import secure_filename, safe_join
from PIL import Image
from io import BytesIO
from app import app
import json
import os
import random


@app.route('/api/head/<string:username>')
def head(username):
  img = Image.open(safe_join(*get_skin_patch(username))).convert("RGBA")
  first_layer = img.crop((8, 8, 16, 16))
  second_layer = img.crop((40, 8, 48, 16))
  first_layer.paste(second_layer, (0, 0), second_layer)
  image_io = BytesIO()
  first_layer.save(image_io, 'PNG')
  image_io.seek(0)
  return send_file(image_io, mimetype="image/png", as_attachment=False, download_name='%s.png' % username)


@app.route('/api/body/<string:username>')
def get_body(username):
  with open(os.path.join(app.config['DATA_DIR'], 'render-cache.json'), encoding='utf-8') as cf:
    '''структура json
    [
    "username":"render_cache",
    ...
    ]
    '''
    caches = json.load(cf)

  skin_path = safe_join(*get_skin_patch(username))
  skin_hash = calculate_file_hash(skin_path)

  render_cache = caches.get(username)

  # рендерим скин если он изменился
  if skin_hash != caches.get(username):

    if render_cache != None:
      render_path = safe_join(app.config['BODY_RENDERS_DIR'], render_cache + '.gif')
      if os.path.exists(render_path):
        os.remove(render_path)
    
    render_cache = update_hash(caches, username, skin_hash)
    render_body(skin_path, render_cache)

  return send_from_directory(app.config['BODY_RENDERS_DIR'], render_cache + '.gif')


@app.route('/api/skin/<string:username>')
def get_skin(username):
  username = secure_filename(username)
  path, name = get_skin_patch(username)
  return send_from_directory(path, name, as_attachment=False)


@app.route('/api/random_floppa')
def random_floppa():
  rand_floppa = random.choice(os.listdir(app.config["FLOPPA_DIR"]))
  return send_from_directory(app.config["FLOPPA_DIR"], rand_floppa)

