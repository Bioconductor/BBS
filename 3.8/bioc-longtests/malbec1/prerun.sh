#!/bin/bash

. ./config.sh

$BBS_HOME/BBS-prerun.py make-central-rdir
$BBS_HOME/BBS-prerun.py upload-meat-info
