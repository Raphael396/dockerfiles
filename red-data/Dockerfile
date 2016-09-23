FROM ubuntu:16.04

MAINTAINER Caleb Johnson <me@calebj.io>

WORKDIR /opt/red/

ARG repo=https://github.com/Twentysix26/Red-DiscordBot
ARG branch=develop
ENV RED_REPO=${repo} RED_BRANCH=${branch}

ADD ${repo}/archive/${branch}.tar.gz /opt/red.tgz

COPY reset_core_data.sh /bin/reset_core_data

RUN tar xzf /opt/red.tgz --strip-components=1 && \
    mv cogs stock_cogs && mv data stock_data && \
    mkdir -p /data/cogs /data/data && \
    cp -rs /opt/red/stock_cogs/* /data/cogs/ && \
    cp -rs /opt/red/stock_data/* /data/data/ && \
    rm -rf /opt/red && mkdir /opt/red

VOLUME /data
