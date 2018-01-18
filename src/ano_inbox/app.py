import email.utils
from flask import Flask, render_template, make_response, request, Response
import os
import re
from smtplib import SMTP
import subprocess
import sys
import tempfile

app = Flask(__name__)

# Static configuration that does not change through the life of this worker:
config = {}
# Code to set this has been moved to the bottom of the file to enhance readability.

@app.route('/')
def entrance():
    if config['all_is_well']:
        return render_template('index.html', \
                               title = config['title'], \
                               recipients = config['recipients'], \
                               have_several_recipients = config['have_several_recipients'])
    else:
        response = make_response(render_template('problem.html'))
        response.status_code = 500
        return response

@app.route("/submit", methods=['POST'])
def submit():
    if config['all_is_well']:
        text = request.form.get('text')
        if text and 0 < len(text.strip()):
            return Response(stream_from_template(text = text, recipients = config['recipients'], action = do_the_sending(text)))
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
    good = '</pre><h2 class="ok">Your message has been sent.</h2><pre>'
    tried_to_send = False
    try:
        yield("Encrypting your message (S/MIME)...")
        encrypt = subprocess.run(["openssl", "smime", "-encrypt", "-text", *config['keyfiles']], encoding="UTF-8", input=text, stdout=subprocess.PIPE)
        if 0 == encrypt.returncode:
            encrypted_message = encrypt.stdout
            heads = "From: {}\r\n".format(config['from_addr'])
            heads += "Subject: {}\r\n".format(config['subject'])
            for r in config['recipients']:
                heads += "To: {}\r\n".format(r)
            heads += "Date: {}\r\n".format(email.utils.formatdate())
            heads += "Message-ID: {}\r\n".format(email.utils.make_msgid())
            yield(" done. Success.\n")
            yield("Connecting to mail server...")
            with SMTP(host = config['smtp_host'], port = 25) as smtp:
                yield(" done. Success.\n")
                yield("Establishing encrypted connection to mail server...")
                smtp.starttls()
                yield(" done. Success. (Server certificate verification not implemented, though.)\n")
                yield("Trying to send the mail...")
                smtp_done = smtp.sendmail(config['from_addr'], config['recipients'], heads + encrypted_message)
                if 0 == len(smtp_done.keys()):
                    yield(" done. Message was accepted.\n" + good)
                else:
                    yield(" done. Partly successfully.\nThe mail has been accepted for some recipient(s), but not all.\n")
                    for not_receiver in smtp_done.keys():
                        yield("Message was NOT accepted for {} with message {} {}\n" \
                              .format(not_receiver, *smtp_done[not_receiver]))
        else:
            sys.stderr.write("ERROR: openssl did not encrypt properly, return value is {}\n".format(encrypt.returncode))
            sys.stderr.flush()
            yield(" failed.\nSorry, could not encode your message.\n")
            yield(not_sent)
    except Exception as ex:
        # This is hacky:
        sys.stderr.write("ERROR CAUGHT: {}: {}\n".format(type(ex), ex.args))
        sys.stderr.flush()
        if tried_to_send:
            yield('\n\nException caught...' + uncertain_wether_sent)
        else:
            yield('\n\nException caught...' + not_sent)
            
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

config['recipients'], config['keyfiles'], config['have_several_recipients'], config['all_is_well'] = handle_mime_keys()

config['title'] = os.environ.get("ano_inbox.title", "Sending anonymous email.")
config['subject'] = os.environ.get("ano_inbox.subject", "Incoming anonymous email.")

config['smtp_host'] = os.environ.get("ano_inbox.smtp_host")
if not config['smtp_host']:
    sys.stderr.write("ERROR: ano_inbox.smtp_host not set.\n")
    config['all_is_well'] = False

config['from_addr'] = os.environ.get("ano_inbox.from_addr")
if not config['from_addr']:
    sys.stderr.write("ERROR: ano_inbox.from_addr not set.\n")
    config['all_is_well'] = False

