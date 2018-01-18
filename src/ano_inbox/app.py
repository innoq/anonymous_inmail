from flask import Flask, render_template, make_response, request, Response
import os
import re
import subprocess
import sys
import tempfile

app = Flask(__name__)

TITLE = os.environ.get("ano_inbox.title", "Sending anonymous email.")

# A rather technical function to retrieve the keys to encrypt against
# out of the environment and to extract the email address from each.
def handle_mime_keys():

    def extract_from_env():
        i = 0
        key = os.environ.get("ano_inbox.key{}".format(i))
        while key:
            yield [i, key]
            i += 1
            key = os.environ.get("ano_inbox.key{}".format(i))

    recipients = []
    keyfiles = []
    # This is a resource leak if workers get restarted, as this is
    # called once for each worker that is created.
    all_is_well = True
    for i, key in extract_from_env():
        keyfilename = None
        with tempfile.NamedTemporaryFile(suffix = ".crt", delete = False) as keyfile:
            keyfile.write(key.encode())
            keyfilename = keyfile.name
        result = subprocess.run(["openssl", "x509", "-noout", "-text", "-in", keyfilename], encoding="UTF-8", stdout=subprocess.PIPE)
        if 0 == result.returncode:
            email = None
            for line in result.stdout.splitlines():
                match = re.match("\s*Subject:.*emailAddress\s*\=\s*([^,]+)(,.*)?$", line)
                if match:
                    email = match.group(1)
            if email:
                recipients.append(email)
                keyfiles.append(keyfilename)
            else:
                all_is_well = False
                sys.stderr.write("ERROR: Ignoring ano_inbox.key{} as no email address could be found.\n{}\n".format(i, result.stdout))
        else:
            all_is_well = False
            sys.stderr.write("ERROR: Ignoring ano_inbox.key{} as openssl couldn't interpret it\n".format(i))
    if 0 == len(recipients):
        sys.stderr.write("ERROR: No keys / emails found.\n")
        all_is_well = False
    sys.stderr.flush()
    have_several_recipients = 1 < len(recipients)
    return [ recipients, keyfiles, have_several_recipients, all_is_well ]

RECIPIENTS, KEY_FILES, HAVE_SEVERAL_RECIPIENTS, ALL_IS_WELL = handle_mime_keys()

@app.route('/')
def entrance():
    if ALL_IS_WELL:
        return render_template('index.html', \
                               title = TITLE, \
                               recipients = RECIPIENTS, have_several_recipients = HAVE_SEVERAL_RECIPIENTS)
    else:
        response = make_response(render_template('problem.html'))
        response.status_code = 500
        return response

@app.route("/submit", methods=['POST'])
def submit():
    if ALL_IS_WELL:
        text = request.form.get('text')
        if text and 0 < len(text.strip()):
            return Response(stream_from_template(text = text, recipients = RECIPIENTS, action = do_the_sending(text)))
        else:
            def please():
                yield("Provide some text, yes?\n\n")
            text_missing = Response(please())
            text_missing.mimetype = "text/plain"
            text_missing.status_code = 400
            return text_missing
    else:
        return make_response(render_template('problem.html')), 500

def stream_from_template(**context):
    app.update_template_context(context)
    template = app.jinja_env.get_template('send.html')
    rv = template.stream(context)
    rv.disable_buffering()
    return rv

def do_the_sending(text):
    not_sent = '</pre><h2 class="oops">Ooops - something bad and unexpected happened.</h2><p class="oops">Your mail never got anywhere.</p><p>We are very sorry indeed!</p><pre>'
    uncertain_wether_sent = '</pre><h2 class="oops">Ooops - something bad and unexpected happened.</h2><p class="oops">It is uncertain whether your mail got through.</p><p>We are very sorry indeed!</p><pre>'
    try:
        yield("Encrypting your message...")
        encrypt = subprocess.run(["openssl", "smime", "-encrypt", "-text", *KEY_FILES], encoding="UTF-8", input=text, stdout=subprocess.PIPE)
        if 0 == encrypt.returncode:
            yield(" done. Success.\n")
            encrypted_message = encrypt.stdout
            yield("Connecting to mail server...")
            
            yield(" functionality not implemented yet. Sorry.\n" + not_sent)
        else:
            sys.stderr.write("ERROR: openssl did not encrypt properly, return value is {}\n".format(encrypt.returncode))
            sys.stderr.flush()
            yield(" failed.\nSorry, could not encode your message.\n")
            yield(not_sent)
    except Exception as ex:
        # This is hacky:
        sys.stderr.write("ERROR CAUGHT: {}: {}\n".format(type(ex), ex.args))
        sys.stderr.flush()
        yield('\n\nException caught...' + uncertain_wether_sent)
    
