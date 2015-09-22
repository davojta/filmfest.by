FROM fedora:22
MAINTAINER Stas Rudakou "stas@garage22.net"

RUN dnf -y update; dnf clean all;
RUN dnf -y install python python-virtualenv gcc postgresql-devel

ENV PYTHONUNBUFFERED 1

RUN useradd -d /app -m filmfest
USER filmfest
RUN virtualenv /app
RUN mkdir /app/src
WORKDIR /app/src

ADD . /app/src/
ADD data.json /app/data.json
RUN /app/bin/pip install --allow-unverified PIL --allow-external PIL -r requirements.txt

ENTRYPOINT ["/app/bin/python", "manage.py"]