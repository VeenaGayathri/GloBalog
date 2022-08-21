from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, session
from flask_login import login_user, current_user, logout_user, login_required
from blog import db, bcrypt,sess
from blog.model import User, Post
from blog.users.forms import (RegisterationForm, LoginForm, UpdateAccountForm,
                                   RequestResetPasswordForm, ResetPasswordForm)
from blog.users.utils import save_pic, send_activation_mail, check_confirmed
import os
from blog.config import Config 
from blog.s3_functions import show_image, create_presigned_url
from flask_session import Session

users=Blueprint('users','__name__') 

@users.route('/confirm/<token>')
def confirm_email(token):
    email = User.confirm_token(token)
    if not email:
        flash('You are trying to access an invalid or expired page. You have to resend confirm email', 'warning')
        return redirect(url_for('users.unconfirmed'))
    logout_user()
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.commit()
        flash('You have confirmed your account. You can now try logging in!', 'success')
    return redirect(url_for('users.login'))

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            confirmed=False
        )
        db.session.add(user)
        db.session.commit()

        token = User.generate_confirmation_token(user.email)
        confirm_url = url_for('users.confirm_email', token=token, _external=True)
        html = render_template('mails/activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_activation_mail(user.email, subject, html)
        
        session["username"] = request.form.get("username")
        login_user(user,remember=True)
        
        flash('An email has been sent with instructions to create your account.', 'info')
        return redirect(url_for('users.unconfirmed'))
    return render_template('users/register.html',title="Register", form=form) # Passing this form to template

@users.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('home')
    flash('Please confirm your account!', 'warning')
    return render_template('users/unconfirmed.html',title='Account Confirmation')


@users.route('/resend_email')
@login_required
def resend_confirmation():
    token = User.generate_confirmation_token(current_user.email)
    confirm_url = url_for('users.confirm_email', token=token, _external=True)
    html = render_template('mails/activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_activation_mail(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('users.unconfirmed'))



@users.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    login_form=LoginForm()
    if login_form.validate_on_submit():
        user=User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,login_form.password.data): # login_form password.data is data read from user input and user.password is data retirieved from database
            #if request.method == "POST":
              # record the user name
            session["username"] = request.form.get("username")
            login_user(user,remember=login_form.remember.data)
            #to login we use flask login_user function, it also takes remember as arg
            flash(f'Hi {user.username}, You are Logged in!', 'success') 
            render_page=request.args.get('next')# value of next parameter indicating next page else it will return none
            return redirect(render_page) if render_page else redirect(url_for("main.home"))
        else:
            flash('Login Unsuccessful. Please check your Email and Password','danger')
    return render_template('users/login.html',title="Login",form=login_form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect(url_for("main.home"))

@users.route('/account',methods=['GET','POST'])
@login_required
@check_confirmed
#we need to login to access this route
#we also need to tell where login route is located so we set login route in __init__ 
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            pic_file_name=save_pic(form.profile_pic.data)
            last_pic=current_user.image_file
            #contents = show_image(BUCKET)
            current_user.image_file=pic_file_name
            if last_pic!='default.jpg':                                 
                file_path=os.path.join(current_app.root_path, 'static/profile_pics', last_pic)
                os.remove(file_path)   
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash("Your account has been updated!",'success')
        return redirect(url_for('users.account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    #url = create_presigned_url(Config.S3_BUCKET,current_user.image_file)
    image_file= url_for('static',filename='profile_pics/'+current_user.image_file)#"{}".format(current_user.image_file)#
    return render_template('users/account.html',title='Account',form=form,image_file=image_file)
    
@users.route('/user/<string:username>')
def user_post(username):
    user=User.query.filter_by(username=username).first_or_404()
    page=request.args.get('page',1,type=int)
    posts=Post.query.filter_by(author=user).order_by(Post.date.desc()).paginate(per_page=5,page=page)
    return render_template('users/user_post.html',posts=posts,user=user)


@users.route('/reset_password',methods=['GET','POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form=RequestResetPasswordForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        token = User.token=user.get_reset_password_token()
        confirm_url = url_for('users.reset_password', token=token, _external=True)
        html = render_template('mails/reset_password_mail.html', confirm_url=confirm_url)
        subject = "Reset Password Request"
        send_activation_mail(user.email, subject, html)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/request_reset_password.html',title='Reset Password',form=form)

@users.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
     if current_user.is_authenticated:
        return redirect(url_for('main.home'))
     user=User.verify_reset_password_token(token=token)
     if not user:
        flash('You are trying to access an invalid or expired page', 'warning')
        return redirect(url_for('users.request_reset_password'))
     form=ResetPasswordForm()
     if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now try logging in', 'success')
        return redirect(url_for('users.login'))
     return render_template('users/reset_password.html',title='Reset Password',form=form)

@users.route('/<string:username>/delete_account',methods=['POST'])#only submit request from modal
@login_required
@check_confirmed
def delete_account_request(username):
    user=User.query.filter_by(username=username).first_or_404()
    if user!=current_user:
        abort(403)#forbidden route
    
    form=UpdateAccountForm()
    form.username.data=current_user.username
    form.email.data=current_user.email
    image_file= current_user.image_file
  
    token = User.generate_delete_token(user.email)
    confirm_url = url_for('users.delete_account', token=token, _external=True)
    html = render_template('mails/delete_account.html', confirm_url=confirm_url)
    subject = "Account Delete Request"
    send_activation_mail(user.email, subject, html)
    flash('An email has been sent with instructions to delete your account.', 'info')
    return render_template('users/account.html',title='Account',form=form,image_file=image_file)


@users.route('/delete_account/<token>',methods=['GET','POST'])
def delete_account(token):
    email = User.confirm_delete_token(token)
    if not email:
        flash('The deletion link is invalid or has expired.', 'danger')
    else:
        user = User.query.filter_by(email=email).first_or_404()
        if user.confirmed:
            db.session.delete(user)
            db.session.commit()
            flash('Your Account has been deleted', 'info')
            return redirect(url_for('users.confirmed_deletion'))
    return redirect (url_for('users.account'))

@users.route('/deleted_account')
def confirmed_deletion():
    return render_template('users/deleted_account.html',title='Deletion Page')

@users.route('/<string:username>/delete_account',methods=['POST'])#only submit request from modal
@login_required
def delete_unconfirmed_account(username):
    user=User.query.filter_by(username=username).first_or_404()
    if user!=current_user:
        abort(403)#forbidden route
    db.session.delete(user)
    db.session.commit()
    flash('Your Account has been deleted', 'info')
    return redirect(url_for('users.confirmed_deletion'))
  
