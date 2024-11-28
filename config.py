import os

basedir = os.path.abspath(os.path.dirname(__name__))

class Config:
  DEBUG =                   os.environ.get('DEBUG')         or "true"
  SECRET_KEY =              os.environ.get('SECRET_KEY')    or 'bezopasno'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  or 'sqlite:///' + os.path.join(basedir, 'app.db')
  UPLOADED_SKINS_DIR =      os.environ.get('SKIN_DIR')      or os.path.join(basedir, 'data/skins')
  ARCHIVE_FILES_DIR =       os.environ.get('ARCHIVE_FILES_DIR') or os.path.join(basedir, 'data/archive')