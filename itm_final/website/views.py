from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Post, User, Comment
from . import db
from sqlalchemy import delete

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", user=current_user)

@views.route('/feed', methods=['GET','POST'])
@login_required
def feed():
    posts = Post.query.all()
    if request.method == "POST":
        department = request.form.get('department')
        course_code = request.form.get('course_code')
        professor = request.form.get('professor')
        post = request.form.get('post')

        if not department:
            flash('Department cannot be empty', category='error')
        elif not course_code:
            flash('Course Code cannot be empty', category='error')
        elif not professor:
            flash('Professor cannot be empty', category='error')
        elif not post:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(post=post, department=department, course_code=course_code, professor=professor, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.feed'))
    query = request.args.get('query')
    if query:
        posts = Post.query.filter(Post.post.contains(query)).all()
    else:
        posts = Post.query.all()

    return render_template('feed.html', user=current_user, posts=posts)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    comment = Comment.query.filter_by(post_id=id).first()
    comments = Comment.query.filter_by(post_id=id).all()

    if not post:
        flash('Post does not exist.', category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this Post.', category='error')
    elif not comment:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')
    else:
        db.session.delete(post)
        db.session.commit()
        for comment in comments:
            db.session.delete(comment)
            db.session.commit()
        flash('Post deleted.', category='success')
        
    return redirect(url_for('views.feed'))

@views.route("/comment/<post_id>", methods=['POST'])
@login_required
def comment(post_id):
    comment = request.form.get('comment')

    if not comment:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(comment=comment, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')
    
    return redirect(url_for('views.feed'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted.', category='success')
        
    return redirect(url_for('views.feed'))

@views.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    posts = Post.query.filter(
        (Post.department.contains(query)) |
        (Post.course_code.contains(query)) |
        (Post.professor.contains(query))
    ).all()

    return render_template('search.html', query=query, results=posts, user=current_user)
