#!/bin/bash

if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit 1
fi

. config.sh

cd $1

. $BBS_HOME/utils/start-virtual-X.sh
$BBS_R_HOME/bin/Rscript $BBS_HOME/utils/compute_coverage.R
. $BBS_HOME/utils/stop-virtual-X.sh
