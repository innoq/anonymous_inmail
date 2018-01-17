import sys
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route("/submit", methods=['POST'])
def submit():
    d = request.form
    sys.stderr.write("Have a POST request\n")
    for k in d.keys():
        sys.stderr.write("{} -> {}\n".format(k, d.getlist(k)))
    return render_template('sent.html')
