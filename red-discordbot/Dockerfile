FROM calebj/red-discordbot:data

RUN apt-get update && \
    apt-get install -y --no-install-recommends libopus0 ffmpeg python3.6 libffi-dev \
                                               git ca-certificates libre2-dev && \
    apt-get install -y python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git clone -b "$RED_BRANCH" --single-branch "$RED_REPO" /opt/red/ && \
    mv cogs stock_cogs && mv data stock_data && \
    ln -s /data/red/cogs && ln -s /data/red/data

COPY run_red.py custom_requirements.txt /opt/red/

RUN pip3 install -r requirements.txt -r custom_requirements.txt

RUN chown -R red:red /data/red /opt/red

USER red

ENTRYPOINT ["/usr/bin/python3.6", "/opt/red/run_red.py"]
