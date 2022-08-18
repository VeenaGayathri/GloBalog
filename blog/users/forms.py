from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from blog.model import User

class RegisterationForm(FlaskForm):
	username= StringField('Username',
		validators=[DataRequired(),Length(min=2,max=20)])
	email= StringField('Email ID',
		validators=[DataRequired(), Email()])
	password= PasswordField('Password',
		validators=[DataRequired(),Length(min=8)])
	confirm_password= PasswordField('Confirm Password',
		validators=[DataRequired(),EqualTo('password')])
	submit=SubmitField('Sign up')

	def validate_username(self,username):
		user=User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("An account with this username already exists, Please try a different one.")
	def validate_email(self,email):
		user=User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("An account with this email already exists, Please try a different one.")

class LoginForm(FlaskForm):
	email= StringField('Email ID',
		validators=[DataRequired(), Email()])
	password= PasswordField('Password',
		validators=[DataRequired()])
	remember=BooleanField('Remember Me')
	submit=SubmitField('Login')

class UpdateAccountForm(FlaskForm):
	username= StringField('Username',
		validators=[DataRequired(),Length(min=2,max=20)])
	email= StringField('Email ID',
		validators=[DataRequired(), Email()])
	profile_pic=FileField('Update Profile Picture',
		validators=[FileAllowed(['jpg','png','jpeg'])])
	
	submit=SubmitField('Update')
	
	def validate_username(self,username):
		if current_user.username!= username.data:
			user=User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError("An account with this username already exists, Please try a different one.")

	def validate_email(self,email):
		if current_user.email!= email.data:
			user=User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError("An account with this email already exists, Please try a different one.")

class RequestResetPasswordForm(FlaskForm):
	email= StringField('Email ID',
		validators=[DataRequired(), Email()])
	submit=SubmitField('Request Password Reset')
	def validate_email(self,email):
		user=User.query.filter_by(email=email.data).first()
		if not user:
			raise ValidationError("An account with this username does not exist, Please try registering first.")
		
class ResetPasswordForm(FlaskForm):
	password= PasswordField('Password',
		validators=[DataRequired(),Length(min=8)])
	confirm_password= PasswordField('Confirm Password',
		validators=[DataRequired(),EqualTo('password')])
	submit=SubmitField('Reset Password')