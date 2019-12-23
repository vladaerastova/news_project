from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Email, Optional, InputRequired
from news_project.models import User
from wtforms.fields.html5 import DateField
import json
from news_project.email import get_validate


class PostForm(FlaskForm):
    heading = StringField('Title', validators=[InputRequired(), Length(max=100)])
    post = TextAreaField('Post body')
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    comment = TextAreaField('Leave a comment', validators=[InputRequired(), Length(max=1000)])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=2, max=50), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=2, max=50), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    username = StringField('Username')
    surname = StringField('Surname')
    birth_date = DateField('Date of birth', validators=[Optional()])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        validation = json.loads(get_validate(email.data).text)
        if validation['result'] != 'deliverable':
            raise ValidationError('Email is incorrect: {}'.format(validation['reason']))





