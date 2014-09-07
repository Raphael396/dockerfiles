#!/bin/bash

if [ -e /.configured ] ; then
	exec /usr/bin/supervisord
fi

# Set up mysql
: ${MSQL_PASS:=$(head -c160 /dev/urandom | tr -dc [:print:] | sed -e 's/ //g' -e "s/'//g" -e 's/"//g' | head -c64 )}
: ${OCDB_PASS:=$(head -c160 /dev/urandom | tr -dc [:print:] | sed -e 's/ //g' -e "s/'//g" -e 's/"//g' | head -c64 )}
/usr/bin/mysqld_safe &
sleep 5
mysqladmin password "${MSQL_PASS}"
/usr/bin/mysql -u root -p "${MSQL_PASS}" -e "CREATE DATABASE owncloud; GRANT ALL ON owncloud.* TO 'owncloud'@'localhost' IDENTIFIED BY \'${OCDB_PASS}\';"
sed -i "s/owncloudsqlpass/${OCDB_PASS}/" /var/www/owncloud/config/autoconfig.php
pkill -f mysqld

if [ -n "${SSH_PUBKEY}" ] ; then # User intends to use ssh
	mkdir -p /root/.ssh/
	echo "${SSH_PUBKEY}" > /root/.ssh/authorized_keys
	echo "SSH server key fingerprints:"
	for pubkey in /etc/ssh/ssh_host_*_key.pub ; do ssh-keygen -lf "$pubkey" ; done
fi

touch /.configured
exec /usr/bin/supervisord
