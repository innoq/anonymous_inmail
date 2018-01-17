FROM python:3.6-stretch

MAINTAINER Andreas Krüger <andreas.krueger@innoq.com>

RUN set -e -x && \
  apt-get update && apt-get -y upgrade && \
  pip install gunicorn Flask && \
  adduser --disabled-password --gecos Application app

ADD ["src", "/home/app"]

WORKDIR /home/app
USER app
EXPOSE 14505
CMD ["gunicorn", "--config", "config.py", "ano_inbox.app:app"]
