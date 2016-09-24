#!/bin/bash

if [ ! -d /var/run/sshd ]; then
    mkdir /var/run/sshd
    chmod 0755 /var/run/sshd
fi

if [ -e /data/ssh ]; then
    mv /etc/ssh /etc/ssh_dist
fi

if [ ! -e /data/ssh ]; then
    mkdir -p /data/ssh
    chown 1000:1000 /data
    ln -s /etc/ssh /data/ssh/config
fi

if [ ! -e /etc/ssh/sshd_config ]; then
    cp -a /etc/ssh_dist/* /etc/ssh/
fi

if [ -e /etc/ssh/sshd_not_to_be_run ]; then
    echo "/etc/ssh/sshd_not_to_be_run present; not starting SSHD"
    exit 0
fi

exec /usr/sbin/sshd $@
