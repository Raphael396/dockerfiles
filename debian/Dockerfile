FROM debian:wheezy
MAINTAINER Caleb Johnson <me@calebj.io>
ADD etc /etc
CMD /config/loop
ENV DEBIAN_FRONTEND noninteractive
RUN useradd -u 500 core
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y ca-certificates inotify-tools nano pwgen supervisor tmux unzip wget cron
RUN apt-get clean
ADD loop /config/loop
RUN chmod +x /config/loop
RUN mkdir -p /config/data /config/init /data /var/log/supervisor
