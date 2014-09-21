FROM calebj/debian:latest
MAINTAINER Caleb Johnson <me@calebj.io>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y lua5.1 prosody

#RUN perl -pi -e "s/daemonize = true;/daemonize = false;/g" /etc/prosody/prosody.cfg.lua
#RUN perl -pi -e "s/allow_registration = false;/allow_registration = true;/g" /etc/prosody/prosody.cfg.lua

RUN mkdir -p /var/run/prosody
RUN chown prosody:prosody /var/run/prosody
# Mount prosody configuration on /etc/prosody and /var/lib/prosody
RUN rm -r /etc/prosody/*

EXPOSE 5222 5269

ADD supervisord.conf /etc/supervisor/conf.d/prosody.conf
