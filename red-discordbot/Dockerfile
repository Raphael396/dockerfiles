FROM calebj/red-discordbot:data

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ca-certificates

RUN git clone -b "$RED_BRANCH" --single-branch "$RED_REPO" /opt/red/ && \
    mv cogs stock_cogs && mv data stock_data && \
    ln -s /data/cogs && ln -s /data/data


RUN apt-get install -y --no-install-recommends libopus0 ffmpeg python3.5 libffi-dev &&\
    apt-get install -y python3-pip

COPY run_red.py custom_requirements.txt /opt/red/

RUN pip3 install -U -r requirements.txt -r custom_requirements.txt

ENTRYPOINT ["/usr/bin/python3.5", "/opt/red/run_red.py"]
