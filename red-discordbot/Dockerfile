FROM ubuntu:16.04

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get install -y --no-install-recommends git libopus0 ffmpeg python3.5 libffi-dev

RUN apt-get install -y python3-pip

WORKDIR /opt/red/

ARG repo=https://github.com/Twentysix26/Red-DiscordBot.git

RUN git clone "${repo}" /opt/red/ && \
    mv cogs stock_cogs && mv data stock_data && \
    mkdir -p /data/cogs /data/data && \
    ln -s /data/cogs && ln -s /data/data && \
    cp -rsbu /opt/red/stock_cogs/* /data/cogs/ && \
    cp -rsbu /opt/red/stock_data/* /data/data/

COPY run_red.py custom_requirements.txt /opt/red/

RUN pip3 install -U -r requirements.txt -r custom_requirements.txt

VOLUME /data

ENTRYPOINT ["/usr/bin/python3.5", "/opt/red/run_red.py"]
