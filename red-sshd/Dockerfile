FROM calebj/red-discordbot:latest

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY sshd.sh /usr/local/bin/red_sshd

RUN mkdir -p /root/.ssh/

ENTRYPOINT ["/usr/local/bin/red_sshd"]

CMD ["-D"]
