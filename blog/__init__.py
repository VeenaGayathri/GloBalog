from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from blog.config import Config 
from flask_s3 import FlaskS3
import boto3, botocore
import flask_assets
from flask_assets import Environment, Bundle
from flask_session import Session
#from Config import S3_BUCKET, S3_KEY, S3_SECRET, S3_LOCATION
import os

"""
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
mail = Mail(app)

"""

#import flask_s3
#>>> from my_application import app
#>>> flask_s3.create_all(app)

db=SQLAlchemy()
#creating database instance, now well create classes or (models) of databases
migrate = Migrate()

bcrypt=Bcrypt()
#hashing library

login_manager=LoginManager()
login_manager.login_view='users.login'
#telling our extension trying to access account where login route is located
login_manager.login_message_category='info'
#to beautify the display using bootstrap , 'info' gives info in blue box

mail=Mail()

s3=FlaskS3()

assets=flask_assets.Environment()

js = Bundle('jquery.js', 'base.js', 'widgets.js',
            filters='jsmin', output='gen/packed.js')

client = boto3.client("s3",
	aws_access_key_id= Config.S3_KEY,
	aws_secret_access_key= Config.S3_SECRET)

sess = Session()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	with app.app_context():
		db.create_all()
	sess.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	migrate.init_app(app, db)
	s3.init_app(app)
	assets.init_app(app)
	assets.register('js_all', js)

	from blog.users.routes import users
	from blog.posts.routes import posts
	from blog.main.routes import main
	from blog.errors.handlers import errors
	app.register_blueprint(users)
	app.register_blueprint(posts)
	app.register_blueprint(main)
	app.register_blueprint(errors)

	return app
