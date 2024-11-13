from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Regexp
from flask_wtf.file import FileRequired, FileAllowed
import sqlalchemy as sa
from app import db
from app.models import User

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

class ChangePasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired("Это поле обязательное!")])
  password2 = PasswordField('Repeat Password', validators=[DataRequired("Это поле обязательное!"), EqualTo('password', "Пароли дожны совпадать!")])
  submit2 = SubmitField('Изменить пароль')

