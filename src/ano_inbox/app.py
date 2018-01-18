import os
import sys
import time
from flask import Flask, render_template, request, Response
app = Flask(__name__)

TITLE = os.environ.get("ano_inbox.title", "Sending anonymous email.")
RECIPIENTS = list(os.environ["ano_inbox.recipients"].split(";"))

@app.route('/')
def hello_world():
    return render_template('index.html', title = TITLE, recipients = RECIPIENTS)

@app.route("/submit", methods=['POST'])
def submit():
    text = request.form['text']
    return Response(stream_from_template(text = text, recipients = RECIPIENTS, action = do_the_sending(text)))

def stream_from_template(**context):
    app.update_template_context(context)
    template = app.jinja_env.get_template('send.html')
    rv = template.stream(context)
    rv.disable_buffering()
    return rv

def do_the_sending(text):
    try:
        yield("Pretending to send...\n")
        time.sleep(1)
        yield("Hard work being done...\n")
        time.sleep(1)
        yield("Done!")
        os.environ['Rumpelstielzchen']
    except Exception as ex:
        # This is hacky:
        sys.stderr.write("ERROR CAUGHT: {}: {}\n".format(type(ex), ex.args))
        sys.stderr.flush()
        yield('\n\nException caught...</pre><h2 class="oops">Ooops - something bad and unexpected happened.</h2><p class="oops">It is uncertain whether your mail got through (probably not).</p><p>We are very sorry indeed!</p><pre>')
    

