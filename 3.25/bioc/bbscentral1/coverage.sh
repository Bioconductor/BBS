#!/bin/bash

. ./config.sh

export COVERAGE_FILE="$BBS_WORK_TOPDIR/COVERAGE.txt"

$BBS_R_HOME/bin/Rscript $BBS_HOME/utils/compute_coverage.R

$BBS_RSYNC_CMD -ave 'ssh -o StrictHostKeyChecking=no' "$COVERAGE_FILE" "$BBS_PUBLISHED_REPORT_DEST_DIR/"
