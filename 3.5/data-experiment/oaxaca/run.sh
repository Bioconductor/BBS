#!/bin/bash

. ./config.sh

VIRTUALX_OUTPUT_FILE="$BBS_WORK_TOPDIR/log/virtual-X.out"
. $BBS_HOME/utils/start-virtual-X.sh
$BBS_HOME/BBS-run.py
. $BBS_HOME/utils/stop-virtual-X.sh
