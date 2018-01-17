# Anonymous Inbox

This allows INNOQ-employees to anonymously send emails to their
bosses.  In essence, this is a very basic web mailer.

## How do we protect from Spam?

The URI and the basic auth credentials are well-known inside the company,
but not published outside.  We occasionally change the credentials.

## How does it work?

You type in an email.  It is never stored anywhere, but immediately
sent to an INNOQ SMTP server.  You can see that while it happens.

## Why is it anonymous?

* Everybody uses the same basic auth credentials.

* You can trust us to never log the IP of the incoming mail (or, if
  you don't, use a coffee shop WiFi, some friend's computer, an
  internet cafe, or [Tor](https://www.torproject.org/)).

## Prerequisites (installation)

Docker.

## Prerequisites (files)

Have a `config.yaml` file in this directory. It should contain (to be
documented).


With that in place, run something like

    docker build -t registry.invalid/anonymous_mailbox .

or, if you are like me and use a local http proxy to speed up repeated
Docker builds:

    docker build --build-arg=http_proxy=http://192.168.0.1:3128/  -t registry.invalid/anonymous_mailbox .

You may need to replace the 192.168.0.1 with the Docker host's IP
used on your machine.