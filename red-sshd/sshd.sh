#!/bin/bash

if [ ! -d /var/run/sshd ]; then
    mkdir /var/run/sshd
    chmod 0755 /var/run/sshd
fi
if [ -e /etc/ssh/sshd_not_to_be_run ]; then
    echo "/etc/ssh/sshd_not_to_be_run present; not starting SSHD"
    exit 0
fi

exec /usr/sbin/sshd $@
