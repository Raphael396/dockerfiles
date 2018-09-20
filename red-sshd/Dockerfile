FROM calebj/red-discordbot:latest

USER root

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends openssh-server vim mc rsync tmux nano \
                                               less netcat-openbsd tzdata coreutils \
                                               xz-utils cpio &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \
           /etc/update-motd.d/60-unminimize /usr/local/sbin/unminimize &&\
    echo Etc/UTC > /etc/timezone

RUN mv /etc/ssh /etc/ssh_dist && \
    rm /etc/ssh_dist/ssh_host_*

COPY sshd.sh /usr/local/bin/red_sshd

COPY userbin.sh /etc/profile.d/

ENTRYPOINT ["/usr/local/bin/red_sshd"]

CMD ["-D"]

EXPOSE 22
