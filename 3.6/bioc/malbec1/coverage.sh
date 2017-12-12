#!/bin/bash

. ./config.sh

export COVERAGE_FILE="$BBS_CENTRAL_RDIR/COVERAGE.txt"

. $BBS_HOME/utils/start-virtual-X.sh
$BBS_R_HOME/bin/Rscript $BBS_HOME/utils/compute_coverage.R
. $BBS_HOME/utils/stop-virtual-X.sh

/usr/bin/rsync -ave 'ssh -o StrictHostKeyChecking=no' "$COVERAGE_FILE" "$BBS_REPORT_DEST_DIR/"
