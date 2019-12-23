from flask import render_template, url_for, flash, redirect, request, jsonify
from news_project import app, bcrypt, db
from news_project.forms import LoginForm, RegistrationForm, PostForm, CommentForm
from news_project.models import User, Role, Post, Comment, user_datastore
from flask_security import Security, roles_required, current_user, login_user, logout_user, login_required
from news_project.token import generate_confirmation_token, confirm_token
from news_project.email import send_email
import os
from sqlalchemy import desc

import json
from collections import OrderedDict
from news_project.admin import admin
import datetime
import time


@app.route('/')
def home():
    posts = Post.query.filter_by(is_approved=True).order_by(desc(Post.date_posted)).all()
    if not posts:
        flash('News feed is empty', 'warning')
    return render_template('home.html', posts=posts, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                user_datastore.commit()
                if user.has_role('admin'):
                    return redirect(url_for('admin.index'))
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
        except:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


security = Security(app, user_datastore)


@app.context_processor
def inject_user():
    return dict(user=current_user)


@security.login_context_processor
def security_login_processor():
    return dict(form=LoginForm())


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=hashed_password, active=True, roles=[Role.query.filter_by(name='user').first()],
                    username=form.username.data, surname=form.surname.data, birth_date=form.birth_date.data, is_confirmed=False)
        db.session.add(user)
        db.session.commit()
        user_datastore.add_role_to_user(user, Role.query.filter_by(name='user').first())
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email.apply_async(args=[user.email, subject, html])
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for("home"))
    return render_template('register.html', title='Register', form=form)


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.is_confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('home'))


@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_confirmed:
        return redirect('home')
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html')


@app.route("/new_post", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if any([not role.need_premoderation for role in current_user.roles]):
            post = Post(title=form.heading.data, content=form.post.data, author=current_user, is_approved=True)
            flash('Post added', 'success')
        else:
            post = Post(title=form.heading.data, content=form.post.data, author=current_user, is_approved=False)
            flash('Post was sending to premoderation', 'success')
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('create_post.html', form=form)


@app.route('/imageuploader', methods=['POST'])
@login_required
def imageuploader():
    file = request.files.get('file')
    if file:
        filename = file.filename.lower()
        f, ext = os.path.splitext(filename)
        if ext in ['.jpg', '.gif', '.png', '.jpeg']:
            folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
            img_fullpath = os.path.join(folder, filename)
            file.save(img_fullpath)
            return jsonify({'location': filename})


def process_html(content):
    new_string = content
    i = content.find('"static/uploads')
    while i > -1:
        new_string = new_string[:i + 1] + '../' + new_string[i + 1:]
        i = new_string.find('"static/uploads')
    return new_string


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    p = Post.query.get_or_404(post_id)
    p.content = process_html(p.content)
    comments = p.comments.order_by(desc(Comment.date_posted)).all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(comment=form.comment.data, commenter=current_user, post=p)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment have been posted', 'success')
        subject = 'Someone has made a comment on newsfeed.com'
        html = render_template('comment_email.html', comment=comment, post=p)
        send_email.apply_async(args=[p.author.email, subject, html])
        return redirect(url_for('post', post_id=p.id))
    return render_template('post.html', post=p, form=form, comments=comments)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))




