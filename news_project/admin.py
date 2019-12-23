from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask import url_for, redirect, request, flash
from flask_admin.contrib.sqlamodel import ModelView
from flask_admin.base import MenuLink
from news_project import app, db, bcrypt
from news_project.models import User, Role, Post, Comment, user_datastore
from flask_security import current_user, logout_user
from sqlalchemy import desc


class UserView(ModelView):
	form_edit_rules = ('roles', 'email', 'username', 'surname', 'active', )

	def on_model_change(self, form, model, is_created):
		if is_created:
			model.password = bcrypt.generate_password_hash(model.password).decode('utf-8')
		model.active = True
		user_datastore.commit()


class MyAdminIndexView(AdminIndexView):

	@expose('/')
	def index(self):
		if not current_user.has_role('admin'):
			return redirect(url_for('login'))
		posts = Post.query.order_by(desc(Post.date_posted)).all()
		for post in posts:
			post.content = process_html(post.content)
		return self.render('admin/index.html', posts=posts)

	@expose('/approve_decline/<int:post_id>', methods=['POST'])
	def approve_decline(self, post_id):
		post = Post.query.get_or_404(post_id)
		post.is_approved = not post.is_approved
		db.session.commit()
		return redirect(url_for('admin.index'))

	@expose('/logout')
	def logout(self):
		logout_user()
		return redirect(url_for('/login'))


def process_html(content):
	new_string = content
	i = content.find('"static/uploads')
	while i > -1:
		new_string = new_string[:i + 1] + '../' + new_string[i + 1:]
		i = new_string.find('"static/uploads')
	return new_string


class LoginMenuLink(MenuLink):

	def is_accessible(self):
		return not current_user.is_authenticated


class LogoutMenuLink(MenuLink):

	def is_accessible(self):
		return current_user.is_authenticated


admin = Admin(app, index_view=MyAdminIndexView(template='admin/index.html'))
# admin = Admin(app)
admin.add_view(UserView(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Comment, db.session))

admin.add_link(LogoutMenuLink(name='Logout', category='', url="/logout"))
