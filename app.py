from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# create a flask instance 
app = Flask(__name__)
# create a csrf token for validation so that hacker can not perform csrf attack
app.config['SECRET_KEY'] = "my_secret_key"


# create a form class 
class NamerForm(FlaskForm):
    name = StringField("What's your Name", validators=[DataRequired()])
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
        
    return render_template('name.html',
                           name=name,
                           form=form)
