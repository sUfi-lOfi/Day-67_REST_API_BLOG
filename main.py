from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

#--------------Database------------------#
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ckeditor = CKEditor(app)


class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

#-----------------Home Route--------------------#
@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.date)).scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route('/<int:post_id>')
def show_post(post_id):
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    return render_template("post.html", post=requested_post)


#------------------Add new post-----------------------#
class AddPost(FlaskForm):
    title = StringField("Blog Post Title",validators = [DataRequired()])
    subtitle = StringField("Subtitle",validators = [DataRequired()])
    author = StringField("Your Name",validators=[DataRequired()])
    img_url = StringField("Image URL",validators=[DataRequired(),URL()])
    body = CKEditorField("Content",validators=[DataRequired()])
    submit = SubmitField("Add post")

@app.route("/add-post",methods=["POST","GET"])
def add_post():
    form = AddPost()
    if form.validate_on_submit():
            blog_post = BlogPost()
            form.populate_obj(blog_post)
            blog_post.date = date.today().strftime("%B %d, %Y")
            db.session.add(blog_post)
            db.session.commit()
            return redirect("/")
    return render_template("make-post.html", form = form,post_action = "Add Post")



#---------------------------Edit post---------------------#
@app.route("/edit-post/<int:post_id>")
def edit_post(post_id):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    form = AddPost(obj = post)
    form.submit.label.text = "Edit Post"
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.commit()
    return render_template("make-post.html",form = form,post_action="Edit Post")



#-----------------------Delete Post--------------------#
@app.route("/delete-post/<int:post_id>")
def delete_post(post_id):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    db.session.delete(post)
    db.session.commit()
    return redirect("/")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
