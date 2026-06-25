from flask import render_template, flash, redirect, url_for, request, send_file, send_from_directory, make_response
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
import os
import json
from urllib.parse import urlsplit, urljoin
from app import app, db
from app.forms import LoginForm, RegistrationForm, SetSkinForm, ChangePasswordForm, ServerForm, ArchiveForm, UserEditForm
from app.models import Archive, ArchiveFile, User, Server
from app.utils import UserRole
from werkzeug.utils import secure_filename, safe_join
import requests

@app.route('/')
@app.route('/index')
def index():
  LAUNCHER_URL = "https://launcher.fl.2bd.net"
  
  return render_template('index.html', launcher_url=LAUNCHER_URL)

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
  data = db.session.execute(sa.select(Archive)).scalars().all()
  if filename is None: 
    return render_template('archive.html', contents=data)

@app.route("/archive/<int:file_id>")
def archive_by_id(file_id):
  file = db.session.get(ArchiveFile, file_id)
  if file is None:
    return 404
  return send_from_directory(app.config["ARCHIVE_FILES_DIR"], file.name, as_attachment=True)

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


def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('У вас нет доступа к админ-панели!', category='error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin')
@login_required
@admin_required
def admin():
    tab = request.args.get('tab', 'users', type=str)
    
    # Get all data
    users = db.session.execute(sa.select(User)).scalars().all()
    servers = db.session.execute(sa.select(Server)).scalars().all()
    archives = db.session.execute(sa.select(Archive)).scalars().all()
    
    return render_template('admin.html', 
                         tab=tab,
                         users=users,
                         servers=servers,
                         archives=archives)


@app.route('/admin/server/add', methods=['POST'])
@login_required
@admin_required
def admin_add_server():
    form = ServerForm()
    if form.validate_on_submit():
        # Check for duplicate IP
        existing_ip = db.session.scalar(sa.select(Server).where(Server.ip == form.ip.data))
        if existing_ip is not None:
            flash('Сервер с таким IP адресом уже существует!', category='error')
            return redirect(url_for('admin', tab='servers'))
        
        server = Server(name=form.name.data, ip=form.ip.data, version=form.version.data, modloader=form.modloader.data, desc=form.desc.data)
        db.session.add(server)
        db.session.commit()
        flash(f'Сервер "{form.name.data}" добавлен!', category='success')
        app.logger.info(f"[{current_user.username}] Добавлен новый сервер: {form.name.data}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', category='error')
    return redirect(url_for('admin', tab='servers'))


@app.route('/admin/server/<int:server_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_server(server_id):
    server = db.session.get(Server, server_id)
    if server is None:
        flash('Сервер не найден!', category='error')
        return redirect(url_for('admin', tab='servers'))
    
    form = ServerForm()
    if form.validate_on_submit():
        # Check if name already exists (but not the current server's name)
        if form.name.data != server.name:
            existing = db.session.scalar(sa.select(Server).where(Server.name == form.name.data))
            if existing is not None:
                flash('Сервер с таким названием уже существует!', category='error')
                return redirect(url_for('admin', tab='servers'))
        
        # Check if IP already exists (but not the current server's IP)
        if form.ip.data != server.ip:
            existing_ip = db.session.scalar(sa.select(Server).where(Server.ip == form.ip.data))
            if existing_ip is not None:
                flash('Сервер с таким IP адресом уже существует!', category='error')
                return redirect(url_for('admin', tab='servers'))
        
        server.name = form.name.data
        server.ip = form.ip.data
        db.session.commit()
        flash(f'Сервер "{form.name.data}" обновлён!', category='success')
        app.logger.info(f"[{current_user.username}] Сервер обновлен: {form.name.data}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', category='error')
    return redirect(url_for('admin', tab='servers'))


@app.route('/admin/server/<int:server_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_server(server_id):
    """Delete server"""
    server = db.session.get(Server, server_id)
    if server is None:
        flash('Сервер не найден!', category='error')
        return redirect(url_for('admin', tab='servers'))
    
    server_name = server.name
    db.session.delete(server)
    db.session.commit()
    flash(f'Сервер "{server_name}" удалён!', category='success')
    app.logger.info(f"[{current_user.username}] Сервер удален: {server_name}")
    return redirect(url_for('admin', tab='servers'))


@app.route('/admin/archive/add', methods=['POST'])
@login_required
@admin_required
def admin_add_archive():
    """Add new archive"""
    form = ArchiveForm()
    if form.validate_on_submit():
        archive = Archive(
            name=form.name.data,
            version=form.version.data or None,
            modloader=form.modloader.data or None,
            description=form.description.data or None
        )
        db.session.add(archive)
        db.session.commit()
        flash(f'Архив "{form.name.data}" добавлен!', category='success')
        app.logger.info(f"[{current_user.username}] Добавлен новый архив: {form.name.data}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', category='error')
    return redirect(url_for('admin', tab='archives'))


@app.route('/admin/archive/<int:archive_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_archive(archive_id):
    """Edit archive"""
    archive = db.session.get(Archive, archive_id)
    if archive is None:
        flash('Архив не найден!', category='error')
        return redirect(url_for('admin', tab='archives'))
    
    form = ArchiveForm()
    if form.validate_on_submit():
        # Check if name already exists (but not the current archive's name)
        if form.name.data != archive.name:
            existing = db.session.scalar(sa.select(Archive).where(Archive.name == form.name.data))
            if existing is not None:
                flash('Архив с таким названием уже существует!', category='error')
                return redirect(url_for('admin', tab='archives'))
        
        archive.name = form.name.data
        archive.version = form.version.data or None
        archive.modloader = form.modloader.data or None
        archive.description = form.description.data or None
        db.session.commit()
        flash(f'Архив "{form.name.data}" обновлён!', category='success')
        app.logger.info(f"[{current_user.username}] Архив обновлен: {form.name.data}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', category='error')
    return redirect(url_for('admin', tab='archives'))


@app.route('/admin/archive/<int:archive_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_archive(archive_id):
    """Delete archive"""
    archive = db.session.get(Archive, archive_id)
    if archive is None:
        flash('Архив не найден!', category='error')
        return redirect(url_for('admin', tab='archives'))
    
    archive_name = archive.name
    db.session.delete(archive)
    db.session.commit()
    flash(f'Архив "{archive_name}" удалён!', category='success')
    app.logger.info(f"[{current_user.username}] Архив удален: {archive_name}")
    return redirect(url_for('admin', tab='archives'))


@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def admin_change_user_role(user_id):
    """Change user role"""
    user = db.session.get(User, user_id)
    if user is None:
        flash('Пользователь не найден!', category='error')
        return redirect(url_for('admin', tab='users'))
    
    if user.id == current_user.id:
        flash('Вы не можете изменить собственную роль!', category='error')
        return redirect(url_for('admin', tab='users'))
    
    role_str = request.form.get('role')
    try:
        new_role = UserRole(role_str)
        user.role = new_role
        db.session.commit()
        flash(f'Роль пользователя "{user.username}" изменена на "{new_role.value}"!', category='success')
        app.logger.info(f"[{current_user.username}] Роль пользователя {user.username} изменена на {new_role.value}")
    except (ValueError, KeyError):
        flash('Неверная роль!', category='error')
    
    return redirect(url_for('admin', tab='users'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Delete user"""
    user = db.session.get(User, user_id)
    if user is None:
        flash('Пользователь не найден!', category='error')
        return redirect(url_for('admin', tab='users'))
    
    if user.id == current_user.id:
        flash('Вы не можете удалить свой аккаунт!', category='error')
        return redirect(url_for('admin', tab='users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'Пользователь "{username}" удалён!', category='success')
    app.logger.info(f"[{current_user.username}] Пользователь удален: {username}")
    return redirect(url_for('admin', tab='users'))