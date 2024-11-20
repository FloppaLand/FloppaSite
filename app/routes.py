from flask import render_template, flash, redirect, url_for, request, send_file, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from io import BytesIO
import os
from PIL import Image, ImageEnhance
from urllib.parse import urlsplit
from base64 import b64encode
from app import app, db
from app.forms import LoginForm, RegistrationForm, SetSkinForm, ChangePasswordForm
from app.models import User
from werkzeug.utils import secure_filename, safe_join

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = db.session.scalar(
    sa.select(User).where(User.username == form.username.data))
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
      next_page = url_for('index')
    return redirect(next_page)
  return render_template('login.html', title='Sign In', form=form)

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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

def get_skin_patch(filename):
   filename = filename + ("" if filename.lower().endswith(".png") else ".png")# проверка на .png
   if os.path.exists(safe_join(app.config['UPLOADED_SKINS_DIR'], filename)):
    return [app.config['UPLOADED_SKINS_DIR'], filename]
   else:
      return [app.config['UPLOADED_SKINS_DIR'], "base.png"]

@app.route('/head/<string:username>')
def head(username):
    img = Image.open(safe_join(get_skin_patch(username))).convert("RGBA") 
    first_layer = img.crop((8, 8, 16, 16))
    second_layer = img.crop((40, 8, 48, 16))
    second_layer = ImageEnhance.Brightness(second_layer).enhance(1.1)
    first_layer.paste(second_layer, (0, 0), second_layer)
    image_io = BytesIO()
    first_layer.save(image_io, 'PNG')
    image_io.seek(0)
    return send_file(image_io, mimetype="image/png", as_attachment=False, download_name='%s.png' % username)

@app.route('/skin/<string:filename>')
def get_skin(filename):
  filename = secure_filename(filename)
  path, name = get_skin_patch(filename)
  return send_from_directory(path, name, as_attachment=False)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    set_skin_form = SetSkinForm()
    change_password_form = ChangePasswordForm()
    formid = request.args.get('formid', 1, type=int)
    if set_skin_form.validate_on_submit() and formid == 1:

      file = set_skin_form.skinfile.data
      file.seek(0) # Нужно после операций с файлом
      file.save(safe_join(app.config['UPLOADED_SKINS_DIR'], current_user.username + ".png"))

      flash("Скин успешно установлен!", category="success_skin")
      app.logger.info(f"[{current_user.username}] Скин изменён")
         
    if change_password_form.submit2.data and change_password_form.validate_on_submit() and formid == 2:
      current_user.set_password(change_password_form.password.data)
      db.session.commit()
      flash("Пароль изменён!", category="success_pass")
      app.logger.info(f"[{current_user.username}] Пароль изменён")
    return render_template('profile.html', change_password_form=change_password_form, set_skin_form=set_skin_form, formid=formid)
   
@app.route('/about')
def about():
   return 'About'
@app.route('/rules')
def rules():
   return 'Rules'

@app.route('/notfound')
def notfound():
    return render_template('notfound.html')

@app.errorhandler(404)
def handle_404_error(error):
    return render_template('notfound.html'), 404