from flask import Flask, render_template, url_for, flash, redirect, request
from flask_behind_proxy import FlaskBehindProxy
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '16bd5547b4e8139970845e9f58c7e470'

# define landing page
@app.route("/")
@app.route("/landing")
def landing():
    return "<p>Welcome to the landing page</p>" 


# define user login page
@app.route("/login")
def login():
    form = LoginForm()

    if form.validate_on_submit():
            
        # Obtain username and password from form
        
        # Check that username is exists, password matches
        
        # If invalid, redirect to login, link to sign up

        return redirect(url_for('home')) 

    return "<p>Welcome to the login page</p>"


# define signup page
@app.route("/signup")
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():
        
        # Obtain username and email data from form
        
        # Check that username and email are unique
        
        # If not unique, redirect to signup page

        # add user data to database

        return redirect(url_for('home')) 
    return "<p>Welcome to the sign up page</p>"


# define home page
@app.route("/home")
def home():
    return "<p>Welcome to the home page</p>"


# define tracking page
@app.route("/tracking")
def tracking():
    return "<p>Welcome to the tracking page</p>"


# define topic expanding page
@app.route("/topic_expand")
def topic_expand():
    return "<p>Welcome to the topic expansion page</p>"

# define bookmarks page
@app.route("/bookmarks")
def bookmarks():
    return "<p>Welcome to the bookmarks page</p>" 


# define route to update_server, connecting git repo to PythonAnywhere
@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/IzMo2000/SproutWealth')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


# define main to run app
if __name__ == '__main__':               
    app.run(debug=True, host="0.0.0.0")