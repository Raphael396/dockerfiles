FROM ubuntu:16.04

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get install -y --no-install-recommends git libopus0 ffmpeg python3.5 libffi-dev

RUN apt-get install -y python3-pip

RUN pip3 install 'git+https://github.com/Rapptz/discord.py@master#egg=discord.py[voice]'

WORKDIR /opt/red/

ARG repo=https://github.com/Twentysix26/Red-DiscordBot.git

RUN git clone "${repo}" /opt/red/ && \
    mv cogs stock_cogs && mv data stock_data && \
    mkdir -p /data/cogs /data/data && \
    ln -s /data/cogs && ln -s /data/data && \
    cp -rsbu /opt/red/stock_cogs/* /data/cogs/ && \
    cp -rsbu /opt/red/stock_data/* /data/data/

VOLUME /data

COPY run_red.py /opt/red/

ENTRYPOINT ["/usr/bin/python3.5", "/opt/red/run_red.py"]
