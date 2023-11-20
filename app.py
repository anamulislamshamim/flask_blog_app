from flask import Flask, render_template, flash, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash


# create database instance 
db = SQLAlchemy()


# create_app function holds all necessary things regarding app and database configuration 
def create_app():
    # create a flask app instance 
    app = Flask(__name__)
    # configure the sqlite3 database 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    # to avoid unnecessary errors with database config the followings
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    # create a csrf token for validation so that hacker can not perform csrf attack
    app.config['SECRET_KEY'] = "my_secret_key"
    # initialize the database for app
    db.init_app(app)
    # push the app context
    app.app_context().push()
    return app


app = create_app()


# migrate the db
migrate = Migrate(app, db)


# Create Database Model. Note: Model is actually nothing but database table.
class Users(db.Model):
    # here specify the fields 
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    badge = db.Column(db.String(100), nullable=True, unique=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # password hashing 
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError('Password is not readable attribute!')
    
    @password.setter 
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password) 
    
    
    def __repr__(self):
        return "<Name %r>" % self.name 


# namer form for /name route 
class NamerForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")


# password form  
class PasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

# create a form class 
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message="Passwords must be match!")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    badge = StringField("Badge")
    submit = SubmitField("Submit")
    

# create necessary routes
# localhost:5000
@app.route("/")
def index():
    pizzas = ['peporoni', 'beef pizza', 'dominos']
    stuff = 'Trigger <script>alert("You have been hacked!");</script>'
    return render_template('index.html', stuff = stuff, pizzas=pizzas)


# localhost:5000/user/john
@app.route('/user_profile/<name>')
def user(name):
    return render_template('user.html', user_name=name)


#create custom error page
# invalid url
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# internal server error 
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


# create a name page 
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None 
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data 
        form.name.data = ''
        flash(f"{name} added successfully!", "info")
        
    return render_template('name.html',
                           name=name,
                           form=form)


# create a name page 
@app.route('/test_password', methods=['GET', 'POST'])
def test_password():
    email = None 
    password = None
    password_to_check = None 
    passed = None 
    
    form =PasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data 
        password = form.password.data 
        form.email.data = ''
        form.password.data = ''
        flash(f"Email & Password submitted successfully!", "info")
        # look up users by email
        password_to_check = Users.query.filter_by(email=email).first()
        
        # check hashed password
        passed = check_password_hash(password_to_check.password_hash, password)
        
    return render_template('test_password.html',
                           email = email, 
                           password = password,
                           password_to_check=password_to_check,
                           passed=passed,
                           form=form)


# create route /user/add for GET and POST methods
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None 
    form = UserForm()
    if form.validate_on_submit():
        # validate whether this email is already exist in our system. If user exist then return the email otherwise will return None 
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # hash the password
            hashed_pass = generate_password_hash(form.password_hash.data)
            user = Users(name=form.name.data, email=form.email.data, badge=form.badge.data, password_hash=hashed_pass) 
            db.session.add(user)
            db.session.commit()
            flash(f"{form.name.data} added successfully!")
        name = form.name.data 
        form.name.data = ""
        form.email.data = ""  
        form.badge.data = "" 
    
    our_users = Users.query.order_by(Users.date_added)
          
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


# create route for update the document 
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.badge = request.form['badge']

        try:
            db.session.commit()
            flash(f"{name_to_update.name}'s data updated successfully!", "info")
            return redirect('/user/add')
        except:
            flash("Something went wrong! Please try again!")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update)


# create route for delete document from the database 
@app.route('/delete/user/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f"{user_to_delete.name} deleted successfully!")
    else:
        flash("User doesn't exist! Somethng went wrong! Please try again!")
        
    return redirect('/user/add')