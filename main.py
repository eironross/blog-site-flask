from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, URLField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import os
from dotenv import load_dotenv


load_dotenv()



'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

'''
ImportError: cannot import name 'url_encode' from 'werkzeug.urls' on the first run try editing the requirements.txt

werkzeug==2.3.3
'''

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.environ.get("SECRET_KEY") 
Bootstrap5(app)

ckeditor = CKEditor()
ckeditor.init_app(app)
# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get("SQLITE__PATH") 
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class AddPostForm(FlaskForm):
    title = StringField("Create a blog title ",validators=[DataRequired()])
    subtitle = StringField("Create a heading",validators=[DataRequired()])
    author = StringField("Enter you name", validators=[DataRequired()])
    new_date = DateField("Enter the date", validators=[DataRequired()])
    img_url = URLField("Paste here a link of an image", validators=[URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])    
    submit= SubmitField("Submit")
# with app.app_context():
#     db.create_all()


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    results = db.session.execute(db.select(BlogPost))
    all_posts = results.scalars().all()
    posts = [ post for post in all_posts ]
    print(posts)
    return render_template("index.html", all_posts=posts)

# TODO: Add a route so that you can click on individual posts.
@app.route('/post', methods=['GET'])
def show_post():
    # TODO: Retrieve a BlogPost from the database based on the post_id
    post = request.args.get("post_id")
    print(post)
    requested_post = db.get_or_404(BlogPost, post)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/addpost', methods=['GET', 'POST'])
def add_new_post():
    form = AddPostForm()
    
    if form.is_submitted():
        pesta = form.new_date.data
        re_date = pesta.strftime("%B %d, %Y")
        
        new_post = BlogPost(
                            title=form.title.data,
                            subtitle=form.subtitle.data,
                            img_url=form.img_url.data,
                            date=re_date,
                            author=form.author.data,
                            body=form.body.data
                            )
        db.session.add(new_post)
        db.session.commit()
        
        print("Sucessfully added the post to the database")
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form)

# TODO: edit_post() to change an existing blog post

@app.route("/edit-post/<int:post_id>", methods=['GET','POST'])
def edit_post(post_id):
    result = db.get_or_404(BlogPost, post_id)
    edit_form=AddPostForm(
        title=result.title,
        subtitle=result.subtitle,
        img_url=result.img_url,
        author=result.author,
        body=result.body
    )
    if edit_form.is_submitted():
        
        result.title = edit_form.title.data
        result.subtitle = edit_form.subtitle.data
        result.img_url = edit_form.img_url.data
        result.author = edit_form.author.data
        result.body = edit_form.body.data
        result.data = edit_form.new_date.data.strftime("%B %d, %Y")
        
        db.session.commit()
        print("Sucessfully edited the post")
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=edit_form, is_edit=True)
    

# TODO: delete_post() to remove a blog post from the database
@app.route('/delete/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    result = db.get_or_404(BlogPost, post_id)
    db.session.delete(result)
    db.session.commit()
    
    print("Sucessfully deleted the post")
    return redirect(url_for('get_all_posts'))
    

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")



if __name__ == "__main__":
    app.run(debug=True, port=5003)
