from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Babygirl112!@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'blogz'

#built a table for my database
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_post = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_post, owner):
        self.blog_title = blog_title
        self.blog_post = blog_post
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#this will take piroirty before seeing everything else
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index',]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#login page 
@app.route('/login', methods=['POST', 'GET'])
def login():
    user_name_error = ''
    password_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if len(username) < 1:
            user_name_error = 'Do I really have to ask?'
            return render_template('login.html', user_name_error=user_name_error)
        if not user:
            user_name_error = 'TRYING TO HACK I SEE!!!!'
            return render_template('login.html', user_name_error=user_name_error)
        if user:
            if user.password != password:
                password_error = "Either you know it or you dont"
                return render_template('login.html', password_error=password_error, username=username)
        if user and user.password == password:
            session['username'] = username
            return redirect('/new-post')
        return render_template('login.html', user_name_error=user_name_error, password_error=password_error)
    else:
        return render_template('login.html')

#signup to get into the blog page
@app.route("/signup", methods=['POST', 'GET'])
def signup():
    user_name_error = ""
    password_error = ""
    v_error = ""
    if request.method == 'POST':
        username = request.form['username']
        username = username.strip(" ")
        password = request.form['password']
        password = password.strip(" ")
        verify = request.form['verify']
        verify = verify.strip(" ")
        user = User.query.filter_by(username=username).first()
        if not user and len(username) >= 3 and len(password) >= 3 and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/new-post')
        if user:
            user_name_error = "Username already exists."
        if len(username) < 3:
            user_name_error = "Username must be more than 2 characters."
        if len(password) < 3:
            password_error = "Password must be more than 2 characters."
        if password != verify:
            v_error = "Passwords don't match"
    return render_template("signup.html", user_name_error=user_name_error, 
            password_error=password_error, v_error=v_error)

# logout page
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

# route to blog
@app.route('/blog', methods = ['POST','GET'])
def home():
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    users = User.query.all()
    
    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id)
        user = User.query.filter_by(id=user_id).first()
        return render_template('user_post.html', posts=posts, user=user, header="User Posts")
    if blog_id:
        post = Blog.query.get(blog_id)
        user = User.query.filter_by(id=post.owner_id).first()
        return render_template('entry_post.html', post=post, user=user)
    print(len(posts))
    
    return render_template('blog.html', posts=posts, header='All Blog Posts', users=users)
        

#route to new blog post
@app.route('/new-post', methods=['POST', 'GET'])
def new_post():
    owner_of_blog = User.query.filter_by(username=session['username']).first()
    blog_title = ''
    blog_post = ''
    title_error = ''
    body_error = ''

#if statements over what gonna or not gonna be posted!
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_post = request.form['blog_post']
        # title error message
        if blog_title == '':
            title_error = 'Title please and Thank You'
        # post error message
        elif blog_post == '':
            body_error = 'Your really gonna leave this blank... add something please'
        else:
            new_blog = Blog(blog_title, blog_post,owner_of_blog)
            db.session.add(new_blog)
            db.session.commit()
            retrieved_id = str(new_blog.id)
            return redirect('/blog?id=' + retrieved_id )

    return render_template('newpost.html', title="New Post", title_error=title_error,
                body_error=body_error, blog_post=blog_post, blog_title=blog_title)

#routes the page to blog
@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users, header='Blog Users')

if __name__ == '__main__':
    app.run()