from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_behind_proxy import FlaskBehindProxy
from forms import RegistrationForm, LoginForm, SearchForm
from database_utility import *
# from flask_login import login_user, logout_user, current_user, login_required

from news import randompopular, search_keyword
#>>>>>>> 9e60eabf43724e7f5234824520fc9084fb34945b

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '16bd5547b4e8139970845e9f58c7e470'

app.static_url_path = '/static'
app.static_folder = 'static'

# define landing page
@app.route("/")
@app.route("/start")
def start():
    return render_template('start.html', subtitle='Starting Screen') 

@app.route("/settings")
def settings():
    
    return render_template('settings.html', subtitle='Starting Screen') 


# define user login page
@app.route("/login", methods=['GET', 'POST'])
def login():

    # grab form data for login
    form = LoginForm()

    # validate login form on submit
    if form.validate_on_submit():
            
        # obtain username and password from form
        username = form.username.data
        password = form.password.data
        
        user_info = get_user_info(username)


        # check for invalid entry
        if not user_info or user_info.password != password:
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        
        session['user_signed_in'] = True
        # password was valid, direct to home
        session['username'] = username
        return redirect(url_for('home')) 

    return render_template('login.html', subtitle='Login', form=form)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if request.method == 'POST' and 'logoutt' in request.form:
        session['user_signed_in'] = False
        session.pop('username', None)
        return redirect(url_for('start'))
    return render_template('logout.html', subtitle='Logout')
    

# define signup page
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # grab form data for signup
    form = RegistrationForm()

    # validate signup form on submit
    if form.validate_on_submit():
        
        # obtain username,mail, and password data from form
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # check for not unique username
        if check_value_exists(User, User.username, username):
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('signup'))

        # check for not unique email
        elif check_value_exists(User, User.email, email):
            flash('Email already registered. Please choose a different one.')
            return redirect(url_for('signup'))

        # add user to registered user database
        add_user(username, email, password)
        session['user_signed_in'] = True

        session['username'] = username
        return redirect(url_for('home', username = username))
    return render_template('signup.html', subtitle='Sign Up', form=form)


# define home page
@app.route("/home", methods=['GET', 'POST'])
def home():
    if 'username' not in session:

        return redirect(url_for('start'))
    
    username = session['username']

    # retrieve searches
    recent_searches = get_recent_searches(username)

    # retrieve topics
    tracked_topics = get_tracked_topics(username)
    
    # generate articles for home page
    populararts = randompopular()

    return render_template("home.html", populararts = populararts, username = username, recent_searches = recent_searches, tracked_topics = tracked_topics)

    

@app.route("/results", methods=['GET', 'POST'])
def results():
    search = ""

    if request.method == 'POST':
        search = request.form['userInput']
        add_search(session['username'],search)

    elif request.method == 'GET':
        search = request.args.get('search_query')

    articles = search_keyword(search)

    username = session['username']

    recent_searches = get_recent_searches(username)

    tracked_topics = get_tracked_topics(username)

    return render_template("results.html", articles = articles, input = search, recent_searches = recent_searches, tracked_topics = tracked_topics)


# define tracking page
@app.route("/tracking", methods=['GET', 'POST'])
def tracking():
    if 'username' not in session:

        return redirect(url_for('start'))
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
    


    return render_template("tracking.html")

@app.route("/track_topic", methods=['POST'])
def track_topic():
    # check for valid post request
    if request.form['topic'] and 'username' in session:

        # store topic name from post request
        topic = request.form['topic']

        # store topic in database, check for failure to add
        if not add_topic(session['username'], topic):
            flash('Topic Limit Exceeded (max 5), or topic is already tracked. You can remove topics \
                   by accessing the tracking menu via the nav bar (top right) or clicking "Tracked Topics" on the left')
        
        else:
            flash(f'"{topic}" was successfully added as a tracked topic')

    return redirect(url_for('home'))


# define topic expanding page
@app.route("/topic_expand", methods=['GET', 'POST'])
def topic_expand():
    if 'username' not in session:

        return redirect(url_for('start'))
    # has same Update/Update Settings/Remove options as tracking pagew
    # going to need to write an external function for those, most likely

    # if next/previous page is clicked

        # goes to next/previous results


    return "<p>Welcome to the topic expansion page</p>"

# define bookmarks page
@app.route("/bookmark", methods=['GET', 'POST'])
def bookmark():
    if 'username' not in session:

        return redirect(url_for('start'))
    # if remove is clicked

        # removes article from bookmarks

    # if next/previous page is clicked

        # goes to next/previous results
    return render_template("bookmark.html")


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
    app.run(debug=True, host="0.0.0.0", port = 5001)