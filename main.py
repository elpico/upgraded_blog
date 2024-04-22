import datetime

from flask import Flask, render_template, redirect, url_for, abort, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, NoResultFound
from typing import List


app = Flask(__name__)
app.config['SECRET_KEY'] = 'This is my not so secret flask key'
Bootstrap5(app)
ckeditor = CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Create Database
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db=SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    user_type: Mapped[str] = mapped_column(String(50), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    #author: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments: Mapped[List["Comment"]] = relationship(cascade="all, delete-orphan")

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    date: Mapped[str] = mapped_column(Text, nullable=False)
    blog_post_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_posts.id"))

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/')
def get_all_posts():

    # TODO: Query the DB for all the posts. Convert the data to a python list.
    posts=[]
    all_posts = BlogPost.query.all()
    posts = [post for post in all_posts]
    return render_template("index.html", all_posts=posts)

@app.route('/<int:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    # TODO: Retrieve a blogpost from teh DB based on the post_id
    try:
        requested_post = BlogPost.query.get_or_404(post_id)

        comment_form = CommentForm()
        comments = []

        if comment_form.validate_on_submit():
            if request.method == "POST":
                try:
                    comment = comment_form.comment.data
                    date_posted = date.today().strftime("%B %d, %Y")
                    blog_id = post_id

                    new_comment = Comment(content=comment,
                                          date=date_posted,
                                          blog_post_id = blog_id)
                    db.session.add(new_comment)
                    db.session.commit()

                except IntegrityError as e:
                    flash("Error occurred adding comment. Try again", "error")
                    db.session.rollback()

        comments = Comment.query.filter_by(blog_post_id=post_id).all()

    except NoResultFound:
        print("nothing found")
        comments = []

    except Exception as e:
        print(f"Exception occurred reading from database {str(e)}")

    return render_template("post.html", post=requested_post, form=comment_form, comments=comments)

# TODO: add_new_post() to create a new blog post
@app.route('/add_new_post', methods=["GET", "POST"])
@login_required
def add_post():

    blog_form = CreatePostForm()

    if blog_form.validate_on_submit():
        if request.method == "POST":
            #if blog_form.validate():
            title = blog_form.title.data
            subtitle = blog_form.subtitle.data
            body = blog_form.body.data
            #author = blog_form.author.data
            author = current_user
            current_date = date.today().strftime("%B %d, %Y")
            #img_url = "https://upload.wikimedia.org/wikipedia/commons/2/26/Polyrhachis_unicuspis_casent0103194_profile_1.jpg"
            img_url = blog_form.img_url.data

            new_post = BlogPost(title=title, subtitle=subtitle, body=body, author=author, date=current_date, img_url=img_url)
            db.session.add(new_post)
            db.session.commit()

            print(f"New post body is {new_post.body}")
            return redirect(url_for('get_all_posts'))
        # else:
        #     # Form validation failed, handle errors
        #     print("Form validation failed")
        #     # You can access individual field errors like this:
        #     print("Title errors:", blog_form.title.errors)
        #     print("Subtitle errors:", blog_form.subtitle.errors)
        #    print("Body errors:", blog_form.body.errors)
    else:
        print("This should be only when GET is invoked")

    return render_template("make-post.html", form=blog_form, edit=False)

# TODO: edit_post() to change an existing blog post
@app.route('/edit_post/<int:post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):

    # retrieve the contents of the blog post
    try:
        blog_data = BlogPost.query.get_or_404(post_id)
    except Exception as e:
        print(f"Exception occurred reading from database {str(e)}")

    blog_form = CreatePostForm()

    if request.method == 'GET':
        if blog_data:
            blog_form.title.data = blog_data.title
            blog_form.subtitle.data = blog_data.subtitle
            blog_form.body.data = blog_data.body
            #blog_form.author.data = blog_data.author
            blog_form.img_url.data = blog_data.img_url

    elif request.method == 'POST':
        if blog_form.validate_on_submit():
            blog_data.title=blog_form.title.data
            blog_data.subtitle=blog_form.subtitle.data
            blog_data.body=blog_form.body.data
            blog_data.author=blog_data.author
            blog_data.img_url=blog_form.img_url.data
            db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))


    return render_template("make-post.html", form=blog_form, edit=True)

# TODO: delete_post() to remove a blog from the datbase - make it a little secure
@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    try:
        blog = db.get_or_404(BlogPost, post_id)

        db.session.delete(blog)
        db.session.commit()
    except Exception as e:
        print(f"Exception occurred reading from database {str(e)}")

    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/register', methods=["GET", "POST"])
def register():

    register_form = RegisterForm()

    if register_form.validate_on_submit():
        if request.method == "POST":
            email = register_form.email.data
            user = register_form.name.data
            clear_password = register_form.password.data

            hashed_password = generate_password_hash(clear_password, method="pbkdf2", salt_length=8)

            try:
                new_user = User(author=user, email=email, password=hashed_password, user_type="blogger")
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)

                return redirect(url_for('get_all_posts'))
            except IntegrityError as e:
                flash('Email already registered. Please login.', 'error')
                db.session.rollback()

    return render_template("register.html", form=register_form)

@app.route('/login', methods=["GET", "POST"])
def login():

    login_form = LoginForm()

    if login_form.validate_on_submit():
        if request.method == "POST":
            email = login_form.email.data
            password = login_form.password.data

            validated_user = User.query.filter_by(email=email).first()

            if validated_user:
                if check_password_hash(validated_user.password, password):
                    login_user(validated_user)
                    flash('Logged in successfully.')
                    return redirect(url_for('get_all_posts'))
                else:
                    flash('User name or password entered incorrectly, please try again', 'error')
            else:
                flash('User name or password entered incorrectly, please try again', 'error')

    return render_template('login.html', form=login_form)

@app.route('/logout', methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True, port=5003)

