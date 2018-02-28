# Anonymous Inbox

This allows employees to anonymously send emails to their bosses.  In
essence, this is a very basic web mailer (send only).

## How to protect from Spam?

The URI and the basic auth credentials are well-known inside the company,
but not published outside.  Occasionally change the credentials.

## How does it work?

You type in an email.  It is never stored anywhere, but immediately
sent to an SMTP server.  You can see that while it happens.

## Why is it anonymous?

* Everybody uses the same basic auth credentials.

* No cookies, sessions, external resources.

* The application never logs the IP of the incoming mail submission
  (If you don't trust that, use a coffee shop WiFi, some friend's computer,
  an internet cafe, or [Tor](https://www.torproject.org/)).

* To guard against spoofing by admins or man-in-the-middle, we do not
  log the text submitted, and also that text is encrypted towards the
  recipients' S/MIME keys.  For the same reason, the subject-line is
  fixed (as that's S/MIME unencrypted in S/MIME-mails), rather than
  set-able by the user.

* However, we don't do HTTPS ourselves (maybe some time we will).  We
  leave that to a reverse proxy in front of us.  So when transiting
  the last yard of network, your data is unencrypted.

## Prerequisites (installation)

Docker.

## Build

With Docker in place, run something like

    docker build -t registry.invalid/anonymous_inbox .

or, if you are like me and use a local http cache to speed up repeated
Docker builds:

    docker build --build-arg=http_proxy=http://192.168.0.1:3128/  -t registry.invalid/anonymous_inbox .

You may need to replace the 192.168.0.1 with the Docker host's IP
used on your machine.

## Environment variables for configuration

`ano_inbox.title` The title to be displayed. Default: "Sending anonymous email."
**The content must be US-ASCII, or sending will fail.**

`ano_inbox.from_addr` What you want to set as the sender address of the mails.

`ano_inbox.subject` The subject line that'll be seen by the recipient(s), default "Incoming anonymous email.".

`ano_inbox.user` `ano_inbox.passwd` The crendentials required (basic auth, not needed for `/health`).

`ano_inbox.smtp_host` The SMTP host we'll use. Make sure it listens on
port 25 and supports starttls.

`ano_inbox.key0`, `ano_inbox.key1`, `ano_inbox.key2`,
`ano_inbox.key3`, ... (at least one): The X.509 certificates of the
people you want to receive the emails.  Their recipient addresses will
be extracted automatically.

We need PEM format, including line breaks and all.  If you have
problems getting line breaks into the environment variables, here are
some ways out:

* If there is no initial `-----BEGIN CERTIFICATE-----` line in such a
  variable's value, but it starts with `https://` (or `http://`, but,
  generally speaking, don't do that), the program will assume a URI,
  will issue a GET request to retrieve the value behind that URI, and,
  if that succeeds, assume what it now has is the key in PEM format
  (again with line breaks and all).  Caveat: **The keys are retrieved
  each time a new worker is started.** So you should keep that key
  server up and running beyond the start of this service.  (You may
  prefer the next option, and use this one only as a means of last
  resort.)
  
* If the value starts with neither `-----BEGIN CERTIFICATE-----`, nor
  `https://`, nor `http://`, the program will attempt to base64-decode
  the value and assume the result is the key in PEM format (again with
  line breaks and all).  So this is the recommendation what to use, if
  you can't put the bare certificate with line breaks into the
  environment variable.

For base64 encoding, you can use the output of the `base64` tool.
This tool is contained in the Docker image you've built.  Run
something like

    docker run --rm -i registry.invalid/anonymous_inbox base64 -w 0 < my-public-cert.pem; echo

and copy the output into the environment variable.  (If you want to
run `base64` locally on a Mac instead, replace `-w 0` with `-b 0`.)

## Run

Something like

    docker run --env=... --publish 80:14505 registry.invalid/anonymous_inbox

(or choose another port instead of the 80 if you already run an HTTP
server on that box).

Point your browser to that server and check the root page shows all
the email addresses, one for each key you provided.
