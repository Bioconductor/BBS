#!/bin/sh
#

set -e  # Exit immediately if a simple command exits with a non-zero status

STATS_HOME=/home/biocadmin/STATS
STATS_REPORT_DIR=/home/biocadmin/public_html/stats

cd $STATS_HOME
rm -rf $STATS_REPORT_DIR/data-experiment
cp main.css $STATS_REPORT_DIR
./mkDownloadStats-for-data-experiment.py

rsync --delete -ave ssh $STATS_REPORT_DIR/ webadmin@master.bioconductor.org:/extra/www/bioc/packages/stats/

