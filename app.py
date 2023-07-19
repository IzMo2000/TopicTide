from flask import Flask, render_template, url_for, flash, redirect, request
from flask_behind_proxy import FlaskBehindProxy

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
    return "<p>Welcome to the login page</p>"


# define signup page
@app.route("/signup")
def signup():
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

if __name__ == '__main__':               
    app.run(debug=True, host="0.0.0.0")


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