import os
class Config:
	#SECRET_KEY = os.urandom(64)
	SECRET_KEY=os.environ.get('secret')
	#SQLALCHEMY_DATABASE_URI='sqlite:///site.db'
	SQLALCHEMY_DATABASE_URI='postgres://payxsludttecnn:1f21ad372f686917511dcf11fec757d59acb97ef11bb335c53811d7eac95bada@ec2-54-164-40-66.compute-1.amazonaws.com:5432/dc70jkdsbjok6m'

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
