from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, URL, Length
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditor, CKEditorField


class CreatePostForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    #author = StringField('Your Name')
    img_url = StringField('Blog Image URL', validators=[DataRequired(), URL()])
    body = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit Post')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Sign me up!')

class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')
    submitfield = SubmitField('Let me in.')

class CommentForm(FlaskForm):
    comment = CKEditorField('Comment', validators=[DataRequired()])
    submit = SubmitField('SUBMIT COMMENT')