FROM python:3.6-stretch

MAINTAINER Andreas Krüger <andreas.krueger@innoq.com>

RUN set -e -x && \
  apt-get update && apt-get -y upgrade && \
  pip install gunicorn Flask && \
  adduser --disabled-password --gecos Application app

ADD ["src", "/home/app"]

WORKDIR /home/app
USER app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app" ]