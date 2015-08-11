#!/bin/sh
#

set -e  # Exit immediately if a simple command exits with a non-zero status

STATS_HOME=/home/biocadmin/STATS
LOGS_LOCAL_PATH=$STATS_HOME/bioc-access-logs
#LOGS_REMOTE_PATH=biocadmin@gopher6:/home/server_logs
LOGS_REMOTE_PATH=biocadmin@rhino01:server_logs

cd $LOGS_LOCAL_PATH
echo ""
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "> RETRIEVING SQUID LOG FILES FROM $LOGS_REMOTE_PATH/cobra"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ""
rsync -ave ssh "$LOGS_REMOTE_PATH/cobra/squid/access.log*" $LOGS_LOCAL_PATH/squid/cobra

echo ""
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "> RETRIEVING SQUID LOG FILES FROM $LOGS_REMOTE_PATH/mamba"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ""
rsync -ave ssh "$LOGS_REMOTE_PATH/mamba/squid/access.log*" $LOGS_LOCAL_PATH/squid/mamba

echo ""
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "> RETRIEVING APACHE2 LOG FILES FROM $LOGS_REMOTE_PATH/krait"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ""
rsync -ave ssh "ubuntu@master.bioconductor.org:/apache2/bioconductor-access.log-*" $LOGS_LOCAL_PATH/apache2/krait

