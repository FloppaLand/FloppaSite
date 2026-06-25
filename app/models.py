from typing import Optional
from datetime import timedelta
from uuid import UUID

import bcrypt
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin

from app import db, login
from app.utils import UserRole


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(16), index=True, unique=True)
    password: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256)) 
    uuid: so.Mapped[Optional[UUID]] = so.mapped_column(sa.UUID(36)) # https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
    role: so.Mapped[UserRole] = so.mapped_column(sa.Enum(UserRole), default=UserRole.USER, nullable=False)
    lastseen: so.Mapped[Optional[timedelta]] = so.mapped_column(sa.Interval)
    playtime: so.Mapped[Optional[timedelta]] = so.mapped_column(sa.Interval)
    
    def set_password(self, password: str):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        if not self.password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader 
def load_user(id):
  return db.session.get(User, int(id))


class Server(db.Model):
  __tablename__ = 'servers'
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
  ip: so.Mapped[str] = so.mapped_column(sa.String(255), index=True, unique=True)
  desc: so.Mapped[str] = so.mapped_column(sa.String(255))
  version: so.Mapped[str] = so.mapped_column(sa.String(8))
  modloader: so.Mapped[str] = so.mapped_column(sa.String(8))

class ArchiveFile(db.Model):
  __tablename__ = 'archive_files'
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  name: so.Mapped[str] = so.mapped_column(sa.String(255))
  label: so.Mapped[str] = so.mapped_column(sa.String(255))
  size: so.Mapped[int] = so.mapped_column(sa.Integer)
  archive_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('archives.id'))

class Archive(db.Model):
  __tablename__ = 'archives'
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
  version: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
  modloader: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
  description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
  period_start: so.Mapped[Optional[timedelta]] = so.mapped_column(sa.Interval)
  period_end: so.Mapped[Optional[timedelta]] = so.mapped_column(sa.Interval)
  files: so.Mapped[list[ArchiveFile]] = so.relationship('ArchiveFile', backref='archive', lazy=True)
  image: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))

