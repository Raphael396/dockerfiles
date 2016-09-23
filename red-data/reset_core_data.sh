#!/bin/bash

tar xzf /opt/red.tgz --strip-components=1
mv cogs stock_cogs && mv data stock_data
find /data -type l -lname '/opt/red/stock_*' -xtype f -delete
cp -rvs --backup=t /opt/red/stock_cogs/* /data/red/cogs/
cp -rvs --backup=t /opt/red/stock_data/* /data/red/data/
rm -rf /opt/red/* .gitignore
