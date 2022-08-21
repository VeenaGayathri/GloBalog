import os, secrets
from PIL import Image
from flask import url_for, current_app
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from blog import mail,client
from functools import wraps
from blog.config import Config 
import boto3


def send_activation_mail(recipients,subject,template):
    msg = Message(
        subject=subject,
        recipients=[recipients],
        html=template,
        sender=f'''{os.environ.get('EMAIL_USER')}'''
    )
    mail.send(msg)


def save_pic(form_pic):
    pic_token=secrets.token_hex(8)
    _,ext=os.path.splitext(form_pic.filename)#files have filename attribute
    savepicname=pic_token+ext
    savepicpath= os.path.join(current_app.root_path, 'static/profile_pics', savepicname)#root path of package directory, os path join to concatenate properly
    
    #form_pic.save(savepicpath)

    req_size=(125,125)
    resized_img=Image.open(form_pic)
    resized_img.thumbnail(req_size)
    resized_img.save(savepicpath)#saved pic in our locn but not yet updated users pic
    
    #output = send_to_s3(file, current_app.config["S3_BUCKET"])
    
    upload_file_bucket = Config.S3_BUCKET
    upload_file_key = 'static/profile_pics/' + str(savepicname)
    client.upload_file(savepicpath, upload_file_bucket, upload_file_key)
    return savepicname
    
    #print(response)
    #return "{}{}".format(Config.S3_LOCATION,savepicname)
    #return response

def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('users.unconfirmed'))
        return func(*args, **kwargs)
    return decorated_function

