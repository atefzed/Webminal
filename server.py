import os, hashlib

from flask import Flask, url_for, render_template, request, flash, redirect, session
from flaskext.sqlalchemy import SQLAlchemy

from wtforms import Form, TextField, PasswordField, BooleanField, validators
from terminal import Terminal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{path}/database.db'.format(path=os.getcwd())

db = SQLAlchemy(app)
shellinabox = Terminal()


class RegistrationForm(Form):
  username = TextField('Username', [validators.Length(min=4, max=25)])
  email = TextField('Email Address', [validators.Length(min=6, max=35)])
  
  password = PasswordField('New Password', [
    validators.Required(),
    validators.EqualTo('confirm', message='Passwords must match')
  ])
  
  confirm = PasswordField('Repeat Password')
  accept_tos = BooleanField('I accept the TOS', [validators.Required()])



class LoginForm(Form):
  username = TextField('Username', [validators.Length(min=4, max=25), validators.Required()])
  password = PasswordField('Password', [validators.Required()])



class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True)
  email = db.Column(db.String(120), unique=True)
  password = db.Column(db.String(120))

  def __init__(self, username, email, password):
    self.email = email
    self.username = username
    self.password = password
    
  def createAccount(self):
    print ' * Creating user "{username}".'.format(username=self.username)
    # ADD USER CREATION CODE HERE
    self.password = hashlib.sha512(
      hashlib.sha512(self.username).hexdigest() + 
      hashlib.sha512(self.password).hexdigest() + 
      hashlib.sha512(self.email).hexdigest()
    ).hexdigest()
    
    print self.password
  
  def __repr__(self):
    return '<User {username}>'.format(username=self.username)



@app.route('/')
def index():
  return 'Navigate to http://127.0.0.1:5001/terminal'



@app.route('/login', methods=['GET', 'POST'])
def login():
  if 'user' in session:
    return redirect(url_for('index'))
  
  form = LoginForm(request.form)
  
  if request.method == 'POST' and form.validate():
    user = User.query.filter_by(username=form.username.data).first()

    if user:
      password_hash = hashlib.sha512(
        hashlib.sha512(user.username).hexdigest() + 
        hashlib.sha512(form.password.data).hexdigest() + 
        hashlib.sha512(user.email).hexdigest()
      ).hexdigest()
      
      if password_hash == user.password:
        session['user'] = user
        
        flash('You have been logged in')
        
        return redirect(url_for('index'))
  
    flash('Invalid username or password')
  
  return render_template('login.html', form=form)



@app.route('/logout')
def logout():
  session.pop('user', None)
  return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
  if 'user' in session:
    return redirect(url_for('index'))
  
  form = RegistrationForm(request.form)
  
  if request.method == 'POST' and form.validate():
    user = User(form.username.data, form.email.data, form.password.data)
    
    db.session.add(user)
    user.createAccount()
    
    db.session.commit()
    
    flash('Thanks for registering')
    
    return redirect(url_for('login'))
  return render_template('register.html', form=form)



@app.route('/terminal')
def terminal():
  return render_template('terminal.html')



if __name__ == '__main__':
  if not shellinabox.process:
    shellinabox.start()
  
  app.secret_key = '\x9a\xa7A\xd0\xd2\xa5\x01v\x1d]\xb3\xc32\x9f\xd1nB)m\xc8\xa1\xf0\xf3\x1f'
  app.debug = True
  app.run()
