import os
from flask import Flask, render_template, session, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_mail import Message

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "My Secret Key!"
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACE_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flaksy]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <kaiyuanddos@163.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')



mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bootstrap = Bootstrap(app)
moment = Moment(app)

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy="dynamic")

    def __repr__(self):
        return "<Role {}>".format(self.name)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class NewForm(FlaskForm):
    name = StringField('What is your name?', validators= [DataRequired()])
    submit = SubmitField('Submit')

def send_mail(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    print("msg body is:{}".format(msg.body))
    print("msg html is:{}".format(msg.html))
    mail.send(msg)

@app.route("/", methods=['GET', 'POST'])
def index():
    form = NewForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            print("app.config['FLASKY_ADMIN'] is:", app.config['FLASKY_ADMIN'] )
            print("app.config['MAIL_USERNAME'] is:", app.config['MAIL_USERNAME'] )
            print("app.config['MAIL_PASSWORD'] is:", app.config['MAIL_PASSWORD'] )
            if app.config['FLASKY_ADMIN']:
                print("begin to send mail")
                send_mail(app.config['FLASKY_ADMIN'], 'New User',
                          'mail/new_user', user=user)
                print("Mail has sent")
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for("index"))
    return render_template('index.html', 
        form=form, name=session.get('name'),
        known=session.get('known', False))

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.route("/user/<name>")
def user(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

