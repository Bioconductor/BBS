#!/bin/sh
#

set -e  # Exit immediately if a simple command exits with a non-zero status

STATS_HOME=/home/biocadmin/STATS

cd $STATS_HOME
rsync -ave ssh webadmin@cobra:'/extra/Backup/log/squid/access.log*' $STATS_HOME/bioc-access-logs/squid/cobra
rsync -ave ssh webadmin@cobra:'/extra/Backup/log/squid/access-bioc.log*' $STATS_HOME/bioc-access-logs/squid/cobra
rsync -ave ssh webadmin@mamba:'/extra/Backup/log/squid/access.log*' $STATS_HOME/bioc-access-logs/squid/mamba
rsync -ave ssh webadmin@krait:'/var/log/apache2/bioconductor-access.log-*' $STATS_HOME/bioc-access-logs/apache2/krait
