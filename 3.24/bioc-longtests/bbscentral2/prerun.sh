#!/bin/bash

. ./config.sh

set -e # Exit immediately if a simple command exits with a non-zero status.

$BBS_PYTHON_CMD $BBS_HOME/BBS-prerun.py make-central-rdir
$BBS_PYTHON_CMD $BBS_HOME/BBS-prerun.py upload-meat-info
