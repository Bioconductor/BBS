#!/bin/bash

. ./config.sh

set -e  # exit immediately if a simple command exits with a non-zero status

$BBS_PYTHON_CMD $BBS_HOME/BBS-run.py STAGE3
$BBS_PYTHON_CMD $BBS_HOME/BBS-run.py STAGE4
