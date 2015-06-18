#!/bin/bash

if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit 1
fi


cd  $1; . config.sh  ; cd -


. ~/BBS/utils/start-virtual-X.sh

time R -q -f ~/BBS/utils/compute_coverage.R


. ~/BBS/utils/stop-virtual-X.sh



 