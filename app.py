from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
# from sqlmodel import Session, select
# from flask_bootstrap import Bootstrap


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.static_folder = 'static'
app.app_context().push()
db = SQLAlchemy(app)
db.init_app(app)



class avrilBlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    subtitle = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.String(20), nullable=False, default='N/A')
    posted_on = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())

    def __repr__(self):
        return self.title


@app.route('/')
@app.route('/home')
@app.route('/avrilWriters')
@app.route("/")
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('new_post'))
    return render_template('login.html', error=error)



@app.route('/blog/<int:id>', methods=['GET', 'POST'])
def blog(id):
    current_post = avrilBlog.query.filter_by(id=id).first_or_404()
    return render_template('blog.html', title='title', current_post=current_post)


@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        post_title = request.form['title']
        post_subtitle = request.form['subtitle']
        post_content = request.form['post']
        post_author = request.form['author']
        new_post = avrilBlog(title=post_title, subtitle=post_subtitle,
                             content=post_content, posted_by=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('new_post.html')


ROWS_PER_PAGE = 2


@app.route('/posts',  methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':
        post_title = request.form['title']
        post_subtitle = request.form['subtitle']
        post_content = request.form['post']
        post_author = request.form['author']
        new_post = avrilBlog(title=post_title, subtitle=post_subtitle,
                             content=post_content, posted_by=post_author)
        db.session.add(new_post)
        db.session.commit()

        return redirect('/posts')
    else:
        page = request.args.get('page', 1, type=int)
        all_posts = avrilBlog.query.order_by(avrilBlog.posted_on).paginate(
            page=page, per_page=ROWS_PER_PAGE)
        return render_template('posts.html', posts=all_posts)


@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    to_edit = avrilBlog.query.get_or_404(id)
    if request.method == 'POST':
        to_edit.title = request.form['title']
        to_edit.subtitle = request.form['subtitle']
        to_edit.author = request.form['author']
        to_edit.content = request.form['post']
        db.session.commit()
        return redirect('/posts')

    else:
        return render_template('edit.html', post=to_edit)


@app.route('/posts/delete/<int:id>')
def delete(id):
    to_delete = avrilBlog.query.get_or_404(id)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/posts')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
