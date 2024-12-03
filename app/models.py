from typing import Optional
from datetime import timedelta
from uuid import UUID
import sqlalchemy as sa
import sqlalchemy.orm as so
from hashlib import md5
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  username: so.Mapped[str] = so.mapped_column(sa.String(16), index=True, unique=True)
  password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
  uuid: so.Mapped[Optional[UUID]] = so.mapped_column(sa.UUID(36)) # https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
  lastseen: so.Mapped[Optional[timedelta]] = so.mapped_column(sa.Interval)
  playtime: so.Mapped[Optional[timedelta]] = so.mapped_column(sa.Interval)
  
  def set_password(self, password):
        self.password_hash = md5(password.encode()).hexdigest()

  def check_password(self, password):
        return self.password_hash == md5(password.encode()).hexdigest()

  def __repr__(self):
    return '<User {}>'.format(self.username)
  
@login.user_loader 
def load_user(id):
  return db.session.get(User, int(id))