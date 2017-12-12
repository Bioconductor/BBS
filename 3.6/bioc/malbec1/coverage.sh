#!/bin/bash

. ./config.sh

. $BBS_HOME/utils/start-virtual-X.sh
$BBS_R_HOME/bin/Rscript $BBS_HOME/utils/compute_coverage.R
. $BBS_HOME/utils/stop-virtual-X.sh
