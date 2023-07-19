from flask import Flask, render_template
app = Flask(__name__)
app.static_url_path = '/static'
app.static_folder = 'static'

@app.route("/")
@app.route("/start")
def start():
    return render_template('start.html', subtitle='Starting Screen')
@app.route("/login")
def login():
    return render_template('login.html', subtitle='Login')
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port = 5001)