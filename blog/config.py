import os
class Config:
	#SECRET_KEY = os.urandom(64)
	SECRET_KEY=os.environ.get('secret')
	SQLALCHEMY_DATABASE_URI='sqlite:///site.db'
	#specifying uri for database and setting it as configuration to set as location, we are using sqlite database, a file on our file system
	#relative path /// located in our folder of project
	MAIL_SERVER='smtp.googlemail.com'
	MAIL_PORT=587
	MAIL_USE_TLS=True
	MAIL_USERNAME=os.environ.get('EMAIL_USER')
	MAIL_PASSWORD=os.environ.get('EMAIL_PASSWORD')
	FLASKS3_BUCKET_NAME=os.environ.get('AWS_STORAGE_BUCKET_NAME')
	S3_BUCKET=os.environ.get('AWS_STORAGE_BUCKET_NAME')
	S3_KEY =os.environ.get('AWS_ACCESS_KEY_ID') 
	S3_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY')
	aws_access_key_id=S3_KEY
	aws_secret_access_key=S3_SECRET
	FLASK_ASSETS_USE_S3=True
	DEFAULT_PIC=f'''https://{S3_BUCKET}.amazonaws.com/static/profile_pics/default.jpeg'''
