from flask import render_template, flash, redirect, url_for, request, send_file, send_from_directory, make_response
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
import os
import json
from urllib.parse import urlsplit, urljoin
from app import app, db
from app.forms import LoginForm, RegistrationForm, SetSkinForm, ChangePasswordForm
from app.models import User
from werkzeug.utils import secure_filename, safe_join
import requests
from mcstatus import JavaServer
import random

@app.route('/')
@app.route('/index')
def index():
  #with open(os.path.join(app.config['DATA_DIR'], 'mc-servers.json'), encoding='utf-8') as f:
  #  metadatas = json.load(f)
  #
  #servers = []
  #
  #for metadata in metadatas:
  #  server = JavaServer.lookup(metadata["ping_ip"])
  #  servers.append({
  #     "status": server.status(),
  #     "query": server.query(),
  #     "meta": metadata
  #     })
  #
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  
  form = LoginForm()
  
  if form.validate_on_submit():
    user = db.session.scalar(
      sa.select(User).where(User.username == form.username.data))

    if user is None or not user.check_password(form.password.data):
      return redirect(url_for('login'))
    
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
      next_page = url_for('index')

    return redirect(next_page)
  
  return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    set_skin_form = SetSkinForm()
    change_password_form = ChangePasswordForm()
    formid = request.args.get('formid', 1, type=int)

    if set_skin_form.validate_on_submit() and formid == 1:
      # Смена скина
      file = set_skin_form.skinfile.data
      file.seek(0) # Нужно после операций с файлом
      file.save(safe_join(app.config['UPLOADED_SKINS_DIR'], current_user.username + ".png"))

      flash("Скин успешно установлен!", category="success_skin")
      app.logger.info(f"[{current_user.username}] Скин изменён")
         
    if change_password_form.submit2.data and change_password_form.validate_on_submit() and formid == 2:
      # Изменение пароля
      current_user.set_password(change_password_form.password.data)
      db.session.commit()
      flash("Пароль изменён!", category="success_pass")
      app.logger.info(f"[{current_user.username}] Пароль изменён")

    if formid == 3: 
      # Импорт скина с офицалки
      response = requests.get("https://mineskin.eu/skin/" + current_user.username)
      filename = safe_join(app.config['UPLOADED_SKINS_DIR'], current_user.username + ".png")
      
      if response.status_code == 200:
        with open(filename, 'wb') as file:
              file.write(response.content)
    return render_template('profile.html', change_password_form=change_password_form, set_skin_form=set_skin_form, formid=formid)

@app.route('/archive')
def archive():
  filename = request.args.get('filename', type=str)
  with open(os.path.join(app.config['DATA_DIR'], 'archive-data.json'), encoding='utf-8') as f:
    data = json.load(f)
  
  if filename is None: 
    return render_template('archive.html', contents=data)
  else:
     filename = secure_filename(filename)
     return send_from_directory(app.config["ARCHIVE_FILES_DIR"], filename)


@app.errorhandler(404)
def handle_404_error(error):
    return render_template('notfound.html'), 404

@app.route("/sitemap")
@app.route("/sitemap.xml")
def sitemap():  
  static_urls = []
  for rule in app.url_map.iter_rules():
      if not str(rule).startswith("/profile") and \
         not str(rule).startswith("/logout") and \
         not str(rule).startswith("/api"):
            url = f"{request.host_url}{str(rule)}"
            static_urls.append(url)

  xml_sitemap = render_template("sitemap.xml", static_urls=static_urls)
  response = make_response(xml_sitemap)
  response.headers["Content-Type"] = "application/xml"

  return response

@app.route("/robots")
@app.route("/robots.txt")
def robots():
  sitemap_url = urljoin(request.host_url, url_for('sitemap'))
  robots_txt = render_template("robots.txt", sitemap_url=sitemap_url)
  response = make_response(robots_txt)
  response.headers["Content-Type"] = "text/plain"

  return response