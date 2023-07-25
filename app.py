from flask import Flask, render_template, url_for, flash, redirect, request, session, render_template_string
from flask_behind_proxy import FlaskBehindProxy
from forms import RegistrationForm, LoginForm, SearchForm, valid_languages, valid_countries 
from database_utility import *
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import json
import ast
import git
import datetime
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

@app.route("/db")
def db():
    with engine.connection() as connection:
        query_result = connection.execute(db.select(database_utility.User))
        print(query_result.fetchall())

@app.route("/settings", methods=['GET', 'POST'])
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
            flash('<span style = "color: rgb(254, 157, 157);">Invalid Username or Password</span>')
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
            flash('<span style = "color: rgb(254, 157, 157);"> Username already exists. Please choose a different one.</span>')
            #flash('<span style="color: red;">"Username already exists. Please choose a different one."</span>', 'error')

            return redirect(url_for('signup'))

        # check for not unique email
        elif check_value_exists(User, User.email, email):
            flash('<span style = "color: rgb(254, 157, 157);"> Email already registered. Please choose a different one.</span>')
            return redirect(url_for('signup'))

        # add user to registered user database
        add_user(username, email, password, 'en', '', '')
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
    user_info = get_user_info(username)
    # retrieve searches
    recent_searches = get_recent_searches(username)

    # retrieve topics
    tracked_topics = get_tracked_topics(username)
    
    # generate articles for home page
    populararts = randompopular(valid_countries[user_info.lang])

    return render_template("home.html", populararts = populararts, username = username, recent_searches = recent_searches, tracked_topics = tracked_topics)


@app.route("/results", methods=['GET', 'POST'])
def results():
    search = ""

    if request.method == 'POST':
        search = request.form['userInput']
        add_search(session['username'],search)

    elif request.method == 'GET':
        search = request.args.get('search_query')

    username = session['username']
    user_info = get_user_info(username)
    print(user_info.lang)

    articles = search_keyword(search, language=user_info.lang, domain=user_info.source)

    recent_searches = get_recent_searches(username)

    tracked_topics = get_tracked_topics(username)

    return render_template("results.html", articles = articles, input = search, recent_searches = recent_searches, tracked_topics = tracked_topics)


# define tracking page
@app.route("/tracking", methods=['GET', 'POST'])
def tracking():
    if 'username' not in session:
        
        return redirect(url_for('start'))

    current_datetime = datetime.datetime.now()
    
    if 'hour' not in session:
        session['hour'] = current_datetime.hour
    
    username = session['username']

    hour = session['hour']

    if current_datetime.hour != hour:
        update_tracked_topics(username)
        session['hour'] = current_datetime.hour

    topic_previews = []

    tracked_topics = get_tracked_topics(username)

    for topic in tracked_topics:
        sub_list = []
        sub_list.append(topic.topic)
        sub_list += get_topic_articles(username, topic.topic, True)
        topic_previews.append(sub_list)

    return render_template("tracking.html", topics = topic_previews)


@app.route("/update_settings", methods=['POST'])
def update_settings():
    if 'username' not in session:
        return redirect(url_for('home'))

    if 'language' in request.form:
        language = valid_languages[request.form['language']]
    else:
        language = 'en'
    
    username = session['username']

    add_settings(username, language, '', '')
    return redirect(url_for('home'))


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
            flash('<span style = "color: rgb(254, 157, 157);font-size:18px;"> Error: Topic Limit Exceeded (max 5), or topic is already tracked. You can remove topics \
                   by accessing the tracking menu via the nav bar (top right) or clicking "Tracked Topics" on the left</span>')
        
        else:
            # add corresponding articles to tracked article database
            for article in articles_list:
                add_article(username, topic, article['url'], article['title'], article['description'], article['urlToImage'])
        
            flash(f'<span style="color: #69FF8C; font-size: 20px;">{topic} was successfully added as a tracked topic</span>')


    return redirect(url_for('home'))

@app.route("/track_bookmark", methods=['POST'])
def track_bookmark():
    if 'username' not in session:
        return redirect(url_for('start'))

    username = session['username']

    topic = request.form['topic']

    redirect_route = request.form['redirect']

    if request.form['article']:
        article = request.form['article']
        article = ast.literal_eval(article)
        url = article['url']
        title = article['title']
        description = article['description']
        thumbnail = article['urlToImage']
    
    else:
        url = request.form['url']
        title = request.form['title']
        description = request.form['description']
        thumbnail = request.form['thumbnail']

    if not add_bookmark(username, url, title, topic,
                                description, thumbnail):
        flash_str = ('<span style="color:rgb(254, 157, 157);font-size: 20px;"> Error: Article already in bookmarks or bookmark limit reached (max 10). You can access your bookmarked articles <a href="/bookmark" >here</a></span>')
    
    else:
        flash_str = ('<span style="color: #69FF8C; font-size: 20px;"> Article successfully added to bookmarks. You can access your bookmarked articles <a href="/bookmark">here</a></span>')

    flash(render_template_string(flash_str))
    
    if redirect != 'home':
        return redirect(url_for(redirect_route, search_query = topic))
    
    return redirect(url_for(redirect_route))
    


# define clear searches route
@app.route("/clear_searches", methods=['POST'])
def clear_searches():
    if 'username' not in session:
        return redirect(url_for('start'))

    username = session['username']

    clear_recent_searches(username)

    flash('<span style="color: #69FF8C; font-size: 20px;"> Recent Searches successfully cleared</span>')

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

    flash(f'<span style = "color: #69FF8C; font-size: 20px;"> "{topic}" successfully removed.</span>')

    return redirect(url_for('tracking'))

@app.route("/untrack_bookmark", methods=['POST'])
def untrack_bookmark():
    if 'username' not in session:
        return redirect(url_for('start'))
    
    username = session['username']

    url = request.form['url']

    remove_bookmark(username, url)

    flash('Article successfully removed from bookmarks.')

    return redirect(url_for('bookmark'))

# define topic expanding page
@app.route("/topic_expand", methods=['GET', 'POST'])
def topic_expand():
    if 'username' not in session:

        return redirect(url_for('start'))
    current_datetime = datetime.datetime.now()
    
    if 'hour' not in session:
        session['hour'] = current_datetime.hour
    
    username = session['username']

    topic = request.args.get('search_query')

    hour = session['hour']

    print(topic)

    if current_datetime.hour != hour:
        update_topic(username, topic)
        session['hour'] = current_datetime.hour
    
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
        repo = git.Repo('/home/TopicTide/TopicTide')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


       
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port = 5002)