from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from blog import db
from blog.model import Post
from blog.posts.forms import PostBlog
from blog.users.utils import send_activation_mail, check_confirmed


posts=Blueprint('posts','__name__') 

@check_confirmed
@posts.route("/post/new", methods=['GET','POST'])
@login_required
def post():
    form=PostBlog()
    if form.validate_on_submit():
        new_post=Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(new_post)#adding something not existing in the database
        db.session.commit()#using only commit for updating something already in the database
        flash("Your Blog has been Posted!",'success')
        return redirect(url_for('main.home'))
    return render_template('posts/post.html',title='Create Blog',form=form,legend='Create a Blog')

@posts.route("/post/<int:post_id>")#passing variable tp route
def specific_post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('posts/specific_post.html',title=post.title,post=post)

@check_confirmed
@posts.route('/post/<int:post_id>/update',methods=['GET','POST'])
@login_required
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!=current_user:
        abort(403)
    form=PostBlog()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash('Your blog has been updated successfully!','success')
        return redirect(url_for('posts.specific_post',post_id=post.id))
    elif request.method=='GET':
        form.title.data=post.title
        form.content.data=post.content
    return render_template('posts/post.html',title='Update Blog',form=form,legend='Update Blog')

@check_confirmed
@posts.route('/post/<int:post_id>/delete_post',methods=['POST'])#only submit request from modal
@login_required
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!=current_user:
        abort(403)#forbidden route
    db.session.delete(post)
    db.session.commit()
    flash('Your blog has been deleted!','success')
    return redirect(url_for('main.home'))


