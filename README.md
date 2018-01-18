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

* To guard against spoofing by admins, we do not log the text submitted,
  and also that text is encrypted towards the recipients' S/MIME keys.

* However, we don't do HTTPS ourselves (maybe some time we will, for
  the time now, it's only a convenience that we don't).  We leave that
  to a reverse proxy in front of us.  So when transiting the last yard
  of network, your data is unencrypted.

## Prerequisites (installation)

Docker.

## Build

With Docker in place, run something like

    docker build -t registry.invalid/anonymous_mailbox .

or, if you are like me and use a local http proxy to speed up repeated
Docker builds:

    docker build --build-arg=http_proxy=http://192.168.0.1:3128/  -t registry.invalid/anonymous_mailbox .

You may need to replace the 192.168.0.1 with the Docker host's IP
used on your machine.

## Environment variables for configuration

`ano_inbox.title` The title to be displayed. Default: "Sending anonymous email."

`ano_inbox.key0`, `ano_inbox.key1` `ano_inbox.key2` `ano_inbox.key3`
(at least one) the X.509 certificates (PEM format, including line
breaks and all) of the people you want to send emails.  Their
recipient addresses will be extracted automatically.

`ano_inbox.smtp_host` The SMTP host we'll use. Make sure it listens on port 25 and supports starttls.

`ano_inbox.from_addr` What you want to set as the sender address of the mails.

`ano_inbox.subject` The subject line that'll be seen by the recipient(s), default "Incoming anonymous email.".

`ano_inbox.user` `ano_inbox.passwd` The crendentials required (basic auth, not needed for `/health`).

## Run

Something like

    docker run --env=... --publish 80:14505 registry.invalid/anonymous_mailbox

(or choose another port instead of the 80 if you already run an HTTP
server on that box).

Point your browser to that server and check the root page shows all
the email addresses, one for each key you provided.

