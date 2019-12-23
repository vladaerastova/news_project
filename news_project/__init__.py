__version__ = '0.1.0'

from flask import Flask
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
import os
basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SECRET_KEY'] = 'da82c72c61d1822e622ac3bd73d700b4'
app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
app.config['SECURITY_LOGIN_URL'] = '/login'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # disable browser cache in dev
app.config['UPLOADED_PATH'] = os.path.join(basedir, '/static/uploads')
mailgun_api_key = os.environ.get('MAILGUN_API_KEY')
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from news_project import routes, errors
