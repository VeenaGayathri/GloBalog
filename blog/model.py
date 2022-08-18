from blog import db, login_manager 
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as serialiser
from flask import current_app
from blog.config import Config
#Usermixin has required attributes and methods required by loadermanager extension to operate
#isauthenticated,isactive,isanonymous,getid methods available in Usermixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#handles sessions on the background for us using 
#reloading userid stored in session for login manager to access it
#login manager decorator for extention as it needs to know where and how to find function 
#returning user with a particular userid


class User(db.Model,UserMixin):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False )
    password=db.Column(db.String(60),unique=True,nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    
    #hashmapped no of password comes to 60 characters
    posts = db.relationship('Post',backref='author',lazy=True)
    #post attribute has relationship to Post class/model
    #backref adds another column to Post model, allows to use author attribute to get user when we create a post
    #lazy defines when sqlalchemy loaads data from database
    #true means all loads at one time

    def generate_confirmation_token(email):
        serializer = serialiser(current_app.config['SECRET_KEY'])
        return serializer.dumps(email, salt='account_activation_salt')
   
    def confirm_token(token, expiration=3600):
        serializer = serialiser(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token,salt='account_activation_salt',max_age=expiration)
        except:
            return False
        return email

    def get_reset_password_token(self):
        s=serialiser(current_app.config['SECRET_KEY'],salt='reset_password_salt')
        return s.dumps({'user_id':self.id})

    @staticmethod #no self
    def verify_reset_password_token(token,expires_in=1800):
        s=serialiser(current_app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token,max_age=expires_in,salt='reset_password_salt')['user_id']
        except:
            return None
        return User.query.get(user_id)

    def generate_delete_token(email):
        serializer = serialiser(current_app.config['SECRET_KEY'])
        return serializer.dumps(email,salt='account_deletion_salt')
    
    def confirm_delete_token(token, expiration=1800):
        serializer = serialiser(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token,salt='account_deletion_salt',max_age=expiration)
        except:
            return False
        return email

    def __repr__(self): #how obj is printed/representer, magic method
        return f"User('{self.username},{self.email},{self.image_file}')"
    #ex: when we'll use User.query.all we will get query in this form


class Post(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow) #not function otherwise it will pass the current time when this code was written
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False) 
    #automatically table names created are lowercase, hence user not User.id

    def __repr__(self): #how obj is printed/representer, magic method
        return f"Post('{self.title}','{self.date}')"


