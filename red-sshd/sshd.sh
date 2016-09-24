#!/bin/bash

if [ ! -d /var/run/sshd ]; then
    mkdir /var/run/sshd
    chmod 0755 /var/run/sshd
fi

mkdir -p /root/.ssh/ /data/ssh

if [ ! -e /data/ssh/sshd_config ]; then
    rm /etc/ssh_dist/ssh_host_* || true
    cp -a /etc/ssh_dist/* /data/ssh/
fi

if [ ! -e /etc/ssh ]; then
    ln -s /data/ssh /etc/ssh
fi

if [ ! -e /etc/ssh/ssh_host_rsa_key ]; then
    dpkg-reconfigure openssh-server
fi

if [ -e /etc/ssh/sshd_not_to_be_run ]; then
    echo "/etc/ssh/sshd_not_to_be_run present; not starting SSHD"
    exit 0
fi

exec /usr/sbin/sshd $@
