from flask import render_template, request, Blueprint
from blog.model import Post,User
import os
from blog.s3_functions import show_image
from blog.config import Config 
from blog.s3_functions import create_presigned_url

main=Blueprint('main','__name__') 

@main.route("/pics")
def list():
    contents = show_image(Config.S3_BUCKET)
    return render_template('main/contents.html', contents=contents)

@main.route('/')
@main.route('/home')
def home():
    
    page=request.args.get('page',1,type=int)#to get page other than first page, default is 1
    posts=Post.query.order_by(Post.date.desc()).paginate(per_page=5,page=page)#posts visibile per page 5 orderby to show newest first so date in descending
    return render_template('main/home.html',posts=posts)#posts has attributes of posts+current page
    #Post.query.paginate(page=2) to display page 2 of paginated display
 
@main.route('/about')
def about():
    return render_template('main/about.html',title="About")

@main.route('/top_users')
def top_users(): 
    users=User.query.all()
    Top_users=[]
    for user in users:
        posts=Post.query.filter_by(author=user).all()
        Top_users.append([user,len(posts)])
    Top_users=sorted(Top_users,key=lambda x: (x[1]),reverse=True)[:5]
    return render_template('main/top_users.html',title='Top Users',users=Top_users)

@main.route('/community')
def community(): 
    users=User.query.all()
    Top_users=[]
    for user in users:
        posts=Post.query.filter_by(author=user).all()
        Top_users.append([user,len(posts)])
    Top_users=sorted(Top_users,key=lambda x: (x[1]),reverse=True)
    return render_template('main/community.html',title='Top Users',users=Top_users)


@main.route('/announcements')
def announcements(): 
    users=len(User.query.all())
    posts=len(Post.query.all())
    return render_template('main/announcements.html',title='Announcements',users=users,posts=posts)

@main.route('/help')
def help():
    mail=Config.MAIL_USERNAME
    return render_template('main/help.html',title='Help',mail=mail)












































