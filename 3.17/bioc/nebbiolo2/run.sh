#!/bin/bash

. ./config.sh

. $BBS_HOME/utils/clean-before-run.sh

$BBS_PYTHON_CMD $BBS_HOME/BBS-run.py no-bin
