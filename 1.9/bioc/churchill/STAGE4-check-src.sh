#!/bin/bash

. ./config.sh

. $BBS_HOME/nodes/$BBS_NODE/start-virtual-X.sh
$BBS_HOME/BBS-run.py STAGE4
. $BBS_HOME/nodes/$BBS_NODE/stop-virtual-X.sh

