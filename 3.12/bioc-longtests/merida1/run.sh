#!/bin/bash

. ./config.sh

$BBS_PYTHON_CMD $BBS_HOME/BBS-run.py STAGE3
$BBS_PYTHON_CMD $BBS_HOME/BBS-run.py STAGE4
