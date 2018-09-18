#!/bin/bash

. ./config.sh

set -e # Exit immediately if a simple command exits with a non-zero status.

$BBS_HOME/BBS-run.py STAGE3
$BBS_HOME/BBS-run.py STAGE4
