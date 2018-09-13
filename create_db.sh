#!/bin/bash


DBNAME="site_manager_db"
DBUSER="siteuser"
DBPASS="password"


OS="$(uname -s)"


if [ $OS == "Darwin" ]; then
    psql -d postgres --command "CREATE USER $DBUSER WITH SUPERUSER PASSWORD '$DBPASS';" && createdb -O $DBUSER $DBNAME
else
sudo -u postgres bash << EOF
    psql --command "CREATE USER $DBUSER WITH SUPERUSER PASSWORD '$DBPASS';" && createdb -O $DBUSER $DBNAME
EOF
fi