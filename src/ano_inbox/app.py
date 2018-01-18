import sys
import time
from flask import Flask, render_template, request, Response
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route("/submit", methods=['POST'])
def submit():
    response = Response(stutter(request.form['text']))
    response.mimetype = "text/plain"
    return response

def stutter(text):
    yield("Getting ready to send your text:\n\n------------------------------\n\n")
    time.sleep(5)
    yield(text)
    time.sleep(5)
    yield("\n\n\n(Not sending yet, sorry.)\n\n")

