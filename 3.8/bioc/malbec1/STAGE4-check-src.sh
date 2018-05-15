#!/bin/bash

. ./config.sh

VIRTUALX_OUTPUT_FILE="$BBS_WORK_TOPDIR/log/virtual-X.out"
$BBS_HOME/BBS-run.py STAGE4
