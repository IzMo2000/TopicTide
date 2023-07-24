from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_behind_proxy import FlaskBehindProxy
from forms import RegistrationForm, LoginForm, SearchForm, valid_languages, valid_countries 
from database_utility import *
import pandas as pd
import json
import ast
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
    if 'username' in session:
        return redirect(url_for('home'))

    return render_template('start.html', subtitle='Starting Screen') 

@app.route("/settings")
def settings():
    lang = valid_languages
    nations = valid_countries 
    return render_template('settings.html', subtitle='Starting Screen', lang = lang, nations = nations) 


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
    
    username = session['username']

    topic_previews = []

    tracked_topics = get_tracked_topics(username)

    for topic in tracked_topics:
        sub_list = []
        sub_list.append(topic.topic)
        sub_list += get_topic_articles(username, topic.topic, True)
        topic_previews.append(sub_list)

    return render_template("tracking.html", topics = topic_previews)

@app.route("/track_topic", methods=['POST'])
def track_topic():

    # check for valid post request
    if 'username' in session:

        username = session['username']

        topic = request.form['topic']

        articles_string = request.form['articles']

        articles_list = ast.literal_eval(articles_string)

        # store topic in database, check for failure to add
        if not add_topic(username, topic):
            flash('Topic Limit Exceeded (max 5), or topic is already tracked. You can remove topics \
                   by accessing the tracking menu via the nav bar (top right) or clicking "Tracked Topics" on the left')
        
        else:
            # add corresponding articles to tracked article database
            for article in articles_list:
                add_article(username, topic, article['url'], article['title'], article['description'], article['urlToImage'])
        
            flash(f'"{topic}" was successfully added as a tracked topic')


    return redirect(url_for('home'))

# define clear searches route
@app.route("/clear_searches", methods=['POST'])
def clear_searches():
    if 'username' not in session:
        return redirect(url_for('start'))

    username = session['username']

    clear_recent_searches(username)

    flash('Recent Searches successfully cleared')

    if request.form['topic']:
        return redirect(url_for('results', search_query = request.form['topic']))

    return redirect(url_for('home'))

# define remove topic page
@app.route("/remove_tracked", methods=['POST'])
def remove_tracked():
    if 'username' not in session:

        return redirect(url_for('start'))
    
    username = session['username']

    topic = request.form['topic']

    remove_topic(username, topic)

    flash(f'"{topic}" successfully removed.')

    return redirect(url_for('tracking'))

@app.route("/remove_bookmark", methods=['POST'])
def remove_bookmark():
    if 'username' not in session:
        return redirect(url_for('start'))
    
    username = session['username']

    remove_id = request.form['id']

    remove_bookmark(id)

    flash(f'Article successfully removed from bookmarks.')

    return redirect(url_for('bookmark'))

# define topic expanding page
@app.route("/topic_expand", methods=['GET', 'POST'])
def topic_expand():
    if 'username' not in session:

        return redirect(url_for('start'))
    
    username = session['username']
    
    topic = request.args.get('expanded_topic')

    tracked_articles = get_topic_articles(username, topic)

    return render_template("expandedkey.html", topic_name = topic, articles = tracked_articles)

# define bookmarks page
@app.route("/bookmark", methods=['GET', 'POST'])
def bookmark():
    if 'username' not in session:

        return redirect(url_for('start'))
    
    username = session['username']

    # get user's bookmarks
    bookmarks = get_bookmarks(username)

    return render_template("bookmark.html", bookmarks = bookmarks)


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
    app.run(debug=True, host="0.0.0.0", port = 5002)