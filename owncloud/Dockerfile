FROM calebj/nginx-php
MAINTAINER Caleb Johnson "me@calebj.io"

RUN echo 'deb http://http.us.debian.org/debian/ wheezy main contrib non-free' > /etc/apt/sources.list
RUN echo 'deb http://download.opensuse.org/repositories/isv:/ownCloud:/community/Debian_7.0/ /' > /etc/apt/sources.list.d/owncloud.list
ADD resources/owncloud-obs.key /tmp/owncloud-obs.key
RUN apt-key add /tmp/owncloud-obs.key && rm /tmp/owncloud-obs.key
RUN apt-get -y update && apt-get install -y apache2 php5 php5-gd php-xml-parser php5-intl php5-sqlite mysql-server-5.5 smbclient curl libcurl3 php5-mysql php5-curl bzip2 wget vim openssl ssl-cert sharutils locales 
owncloud git supervisord openssh-server

# Configure locales
RUN locale-gen en_US en_US.UTF-8
RUN dpkg-reconfigure locales

# Configure MySQL
ADD resources/cfgmysql.sh /tmp/
RUN chmod +x /tmp/cfgmysql.sh
RUN /tmp/cfgmysql.sh
RUN rm /tmp/cfgmysql.sh

ADD resources/etc/ /etc/

RUN a2ensite 001-owncloud
RUN a2dissite 000-default
RUN a2enmod rewrite ssl
RUN a2dismod negotiation

# Add config
ADD resources/var/www/owncloud/ /var/www/owncloud/
RUN chown -R www-data:www-data /var/www/owncloud

EXPOSE 22 443

CMD ["/start.sh"]
