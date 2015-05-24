#!/bin/sh
#

set -e  # Exit immediately if a simple command exits with a non-zero status

STATS_HOME=/home/biocadmin/STATS
#SERVER_LOGS_PATH=biocadmin@gopher6:/home/server_logs
SERVER_LOGS_PATH=biocadmin@rhino1:server_logs

cd $STATS_HOME
echo ""
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "> RETRIEVING SQUID LOG FILES FROM $SERVER_LOGS_PATH/cobra"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ""
rsync -ave ssh "$SERVER_LOGS_PATH/cobra/squid/access.log*" $STATS_HOME/bioc-access-logs/squid/cobra

echo ""
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "> RETRIEVING SQUID LOG FILES FROM $SERVER_LOGS_PATH/mamba"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ""
rsync -ave ssh "$SERVER_LOGS_PATH/mamba/squid/access.log*" $STATS_HOME/bioc-access-logs/squid/mamba

echo ""
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "> RETRIEVING APACHE2 LOG FILES FROM $SERVER_LOGS_PATH/krait"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ""
rsync -ave ssh "$SERVER_LOGS_PATH/krait/apache2/bioconductor-access.log-*" $STATS_HOME/bioc-access-logs/apache2/krait

