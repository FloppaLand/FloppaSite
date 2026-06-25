from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, SelectField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Regexp, Optional
from flask_wtf.file import FileRequired, FileAllowed
import sqlalchemy as sa
from app import db
from app.models import User, Server, Archive
from app.utils import UserRole
from PIL import Image
import re

class LoginForm(FlaskForm):
  username = StringField('Ник', validators=[DataRequired("Это поле обязательное!")])
  password = PasswordField('Пароль', validators=[DataRequired("Это поле обязательное!")])
  remember_me = BooleanField('Запомнить меня')
  submit = SubmitField('Войти')

  def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is None:
            raise ValidationError('Пользователь не найден!')

class RegistrationForm(FlaskForm):
    username = StringField('Ник', validators=[DataRequired("Это поле обязательное!"), Regexp(r'^[a-zA-Z0-9_]{3,16}$', 
                                                                     message="Недопустимое имя пользователя! Используйте только цифры (0-9), латинские буквы (a-z) или подчёркивание(_) от 3 до 16 символов")])
    password = PasswordField('Пароль', validators=[DataRequired("Это поле обязательное!")])
    password2 = PasswordField('Пароль2', 
                              validators=[DataRequired("Это поле обязательное!"), EqualTo('password', "Пароли дожны совпадать!")])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Имя занято! Используйте другое.')

class SetSkinForm(FlaskForm):
    skinfile = FileField(validators=[FileAllowed(['png'], 'Неправельный файл скина!'), FileRequired('Не выбран файл!')])
    submit1 = SubmitField('Загрузить')

    def validate_skinfile(form, field):
        try:
            img = Image.open(field.data)
            img.verify()
        except:
            raise ValidationError("Файл скина повреждён")
        if img.size != (64, 64): # Проверка размера скина. Должно быть 64x64 px
            raise ValidationError("Скин должен быть размером 64x64 px")
       

class ChangePasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired("Это поле обязательное!")])
  password2 = PasswordField('Repeat Password', validators=[DataRequired("Это поле обязательное!"), EqualTo('password', "Пароли дожны совпадать!")])
  submit2 = SubmitField('Изменить пароль')


# Admin Panel Forms

class ServerForm(FlaskForm):
    name = StringField('Название сервера', validators=[DataRequired("Название обязательно!")])
    ip = StringField('IP адрес', validators=[DataRequired("IP адрес обязателен!")])
    version = StringField('Версия', validators=[DataRequired("Версия обязательна!")])
    modloader = StringField('Загузчик', validators=[DataRequired("Выберете загрузчик!")])
    desc = StringField('Описание')

    submit = SubmitField('Сохранить сервер')

    def validate_ip(self, ip):
        # Allow IP:port or just IP format
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}(:\d+)?$'
        if not re.match(ip_pattern, ip.data):
            raise ValidationError('Неверный формат IP адреса! Используйте формат: 192.168.1.1 или 192.168.1.1:25565')
        
        # Validate octets
        parts = ip.data.split(':')
        octets = parts[0].split('.')
        for octet in octets:
            try:
                val = int(octet)
                if val < 0 or val > 255:
                    raise ValidationError('IP адрес содержит недопустимые значения (0-255)!')
            except ValueError:
                raise ValidationError('Неверный формат IP адреса!')

    def validate_name(self, name):
        server = db.session.scalar(sa.select(Server).where(Server.name == name.data))
        if server is not None:
            raise ValidationError('Сервер с таким названием уже существует!')


class ArchiveForm(FlaskForm):
    name = StringField('Название архива', validators=[DataRequired("Название обязательно!")])
    version = StringField('Версия', validators=[Optional()])
    modloader = StringField('Модloader', validators=[Optional()])
    description = TextAreaField('Описание', validators=[Optional()])
    submit = SubmitField('Сохранить архив')

    def validate_name(self, name):
        archive = db.session.scalar(sa.select(Archive).where(Archive.name == name.data))
        if archive is not None:
            raise ValidationError('Архив с таким названием уже существует!')


class UserEditForm(FlaskForm):
    username = StringField('Ник', render_kw={'readonly': True})
    role = SelectField('Роль', choices=[
        ('user', 'Пользователь'),
        ('mod', 'Модератор'),
        ('admin', 'Администратор')
    ])
    submit = SubmitField('Обновить роль')

