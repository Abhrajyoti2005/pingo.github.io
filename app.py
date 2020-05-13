from flask import *
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_mail import *
import json


localhost_server=True
with open("config.json","r") as f:
    params=json.load(f)['params']

app=Flask(__name__)
app.secret_key='super-secret-key'
if (localhost_server):
    app.config['SQLALCHEMY_DATABASE_URI']=params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI']=params['prod_uri']
db=SQLAlchemy(app)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['mail_username'],
    MAIL_PASSWORD=params['mail_password']
)
Mail=Mail(app)

class Contacts(db.Model):
    ID = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Phone_num = db.Column(db.String(50),nullable=False)
    Email = db.Column(db.String(50),nullable=False)
    Message = db.Column(db.Text,nullable=True)
    Date =db.Column(db.DateTime,nullable=False, default=datetime.datetime.now())

class Posts(db.Model):
    ID = db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(50),nullable=False)
    Subject=db.Column(db.String(80),nullable=False)
    Content=db.Column(db.Text,nullable=True)
    Slug=db.Column(db.String(50),nullable=True)
    Datetime=db.Column(db.DateTime,nullable=True,default=datetime.datetime.now())

class Loggers(db.Model):
    ID=db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(200), nullable=False)
try:
    @app.route("/")
    def main():
        return redirect(url_for("dashboard"))


    @app.route("/dashboard",methods=['POST','GET'])
    def dashboard():
            if 'user' in session:
                posts=Posts.query.all()
                user=session['user']
                return render_template("index.html",params=params,posts=posts,user=user)
            if 'admin' in session and 'pass' in session:
                posts=Posts.query.all()
                admin=session['admin']
                return render_template("dashboard.html",posts=posts,params=params,user=admin)

            if request.method=='POST':
                Username=request.form.get('User_name')
                Password=request.form.get('User_pass')
                if (Username==params['admin'] and Password==params['admin_pass']):
                    session['admin']=Username
                    session['pass']=Password
                    posts = Posts.query.all()
                    return render_template("dashboard.html",posts=posts,params=params)
                else:
                    session['user']=Username
                    user=session['user']
                    entry=Loggers(Name=Username,Password=Password)

                    db.session.add(entry)
                    db.session.commit()
                    return render_template("index.html",params=params,user=user)
            return render_template("login.html", params=params)
    @app.route("/edit/<string:ID>", methods=['GET','POST'])
    def edit(ID):
        if request.method=='POST':
            Name=request.form.get('Name')
            Subject=request.form.get('Subject')
            Content=request.form.get('Content')
            Slug=request.form.get('Slug')
            Datetime=datetime.datetime.now()
            if ID==0:
                pass
            else:
                post=Posts.query.filter_by(ID=ID).first()
                post.Name=Name
                post.Subject=Subject
                post.Content=Content
                post.Slug=Slug
                post.Datetime=Datetime
                db.session.commit()
                return redirect("/website")
        post=Posts.query.filter_by(ID=ID).first()
        return render_template("edit.html",params=params,post=post)
    @app.route("/dashboard/<string:ID>",methods=['GET','POST'])
    def delete(ID):
        if request.method=='GET':
            if 'admin' in session:
                post=Posts.query.filter_by(ID=ID).first()
                db.session.delete(post)
                db.session.commit()
                return redirect("/dashboard")
        return render_template("/dashboard")
    @app.route("/logout")
    def logout():
        if 'user' in session:
            session.pop('user')
        if 'admin' in session:
            session.pop('admin')
            session.pop('pass')
        return redirect(url_for("dashboard"))
    @app.route("/contact",methods=['GET','POST'])
    def about():
        """
        IF the server returns some data then only the app will fetch the data otherwise it will not
        """
        if (request.method == 'POST'):
            '''Add entry to the database'''
            Name= request.form.get('Name')
            Email = request.form.get('Email')
            Phone_num = request.form.get('Phone_num')
            Message = request.form.get('Message')

            entry = Contacts(Name=Name,Phone_num=Phone_num,Email=Email,Message=Message,Date=datetime.datetime.now())
            db.session.add(entry)
            db.session.commit()
            try:
                Mail.send_message(f'New message from {Name}',
                                  sender=Email,
                                  recipients=[params['mail_username']],
                                  body=f"Sir, \n\t{Message}\n\nContact Me\n{Email}"
                                  )
            except:
                return render_template("error.html")
        return render_template("contact.html",params=params)
    @app.route("/designblog",methods=['GET','POST'])
    def design_blog():
        if request.method=='POST':
            Name=request.form.get('Name')
            Subject = request.form.get('Subject')
            Content = request.form.get('Content')
            Slag = request.form.get('Slag')
            entry=Posts(Name=Name,Subject=Subject,Content=Content,Slug=Slag)
            db.session.add(entry)
            db.session.commit()
        return render_template("form_blog.html",params=params)
    @app.route("/website")
    def post_func():
        post=Posts.query.all()
        return render_template("website.html",params=params,post=post)
    @app.route("/post/<string:slug_post>",methods=['GET'])
    def blog_posts(slug_post):
        post=Posts.query.filter_by(Slug=slug_post).first()
        return render_template("blog.html",post=post)
    def user():
        return render_template("layout.html",user=session['user'])
except Exception as e:
    @app.route("/error")
    def error():
       return render_template("error.html",error=e)

app.run(debug=True)