from flask import Flask, render_template, url_for, flash, redirect, request
from flask_behind_proxy import FlaskBehindProxy
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '16bd5547b4e8139970845e9f58c7e470'

app.static_url_path = '/static'
app.static_folder = 'static'

# define landing page
@app.route("/")
@app.route("/start")
def start():
    # if signup button is pressed

        # redirect to signup page

    # if login button is pressed

        # redirect to login page

    return render_template('start.html', subtitle='Starting Screen') 


# define user login page
@app.route("/login")
def login():

    # grab form data for login
    form = LoginForm()

    # if login button is pressed

        # redirect to login page

    # validate login form on submit
    if form.validate_on_submit():
            
        # obtain username and password from form
        
        # check that username is exists, password matches
        
        # If invalid, redirect to login, link to sign up

        return redirect(url_for('home')) 

    return render_template('login.html', subtitle='Login')


# define signup page
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # grab form data for signup
    form = RegistrationForm()

    # if sign up button is pressed

        # redirect to sign up page

    # validate signup form on submit
    if form.validate_on_submit():
        
        # obtain username and email data from form
        
        # check that username and email are unique
        
        # if not unique, redirect to signup page

        # add user data to database

        return redirect(url_for('home')) 
    return "<p>Welcome to the sign up page</p>"


# define home page
@app.route("/home", methods=['GET', 'POST'])
def home():
    # grab form data for news search
    form = SearchForm()

    # if track button is pressed

        # search bar topic is not empty

            # send tracking data to database

        # search bar topic is empty

            # indicate error
    
    # if tracked topic title is clicked

        # redirect to tracking page
    
    # if specific tracked topic is clicked

        # redirect to topic expansion

    # validate search form on submit
    if form.validate_on_submit():

        # make call to api to retrieve news stories based on form

        # display stories onto page

        # update recent searches section

    return "<p>Welcome to the home page</p>"


# define tracking page
@app.route("/tracking", methods=['GET', 'POST'])
def tracking():
    # if specific tracked topic is clicked

        # redirect to topic expansion
    
    # if Update is clicked

        # immediately update news stories, display new results
    
    # if Update Settings is clicked

        # revalidate entered settings

            # add new settings to database
    
    # if Remove is clicked

        # removes tracked topic from database

    # if next/previous page is clicked

        # goes to next/previous results
    


    return "<p>Welcome to the tracking page</p>"


# define topic expanding page
@app.route("/topic_expand", methods=['GET', 'POST'])
def topic_expand():
    # has same Update/Update Settings/Remove options as tracking pagew
    # going to need to write an external function for those, most likely

    # if next/previous page is clicked

        # goes to next/previous results


    return "<p>Welcome to the topic expansion page</p>"

# define bookmarks page
@app.route("/bookmarks", methods=['GET', 'POST'])
def bookmarks():
    # if remove is clicked

        # removes article from bookmarks

    # if next/previous page is clicked

        # goes to next/previous results
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
