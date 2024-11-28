import os

basedir = os.path.abspath(os.path.dirname(__name__))

class Config:
  DEBUG =                   os.environ.get('DEBUG')         or "true"
  SECRET_KEY =              os.environ.get('SECRET_KEY')    or 'bezopasno'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  or 'sqlite:///' + os.path.join(basedir, 'app.db')
  DATA_DIR =                os.environ.get('DATA_DIR')      or os.path.join(basedir, 'data/')
  UPLOADED_SKINS_DIR =      os.environ.get('SKIN_DIR')      or os.path.join(DATA_DIR, '/skins')
  ARCHIVE_FILES_DIR =       os.environ.get('ARCHIVE_FILES_DIR') or os.path.join(DATA_DIR, '/archive')