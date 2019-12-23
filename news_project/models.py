from news_project import db, login_manager
from datetime import datetime
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from sqlalchemy.orm import backref


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    need_premoderation = db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    username = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    active = db.Column(db.Boolean())
    is_confirmed = db.Column(db.Boolean())
    posts = db.relationship('Post', backref=backref('author', passive_deletes=True), lazy=True)
    comments = db.relationship('Comment', backref=backref('commenter', passive_deletes=True), lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return self.email


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    is_approved = db.Column(db.Boolean())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    comments = db.relationship('Comment', backref=backref('post', passive_deletes=True), lazy='dynamic')

    def __repr__(self):
        return self.title


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(1000), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
