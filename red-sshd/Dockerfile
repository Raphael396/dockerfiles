FROM calebj/red-discordbot:latest

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server vim mc rsync tmux &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mv /etc/ssh /etc/ssh_dist && \
    rm /etc/ssh_dist/ssh_host_*

COPY sshd.sh /usr/local/bin/red_sshd

COPY userbin.sh /etc/profile.d/

ENTRYPOINT ["/usr/local/bin/red_sshd"]

CMD ["-D"]

EXPOSE 22
