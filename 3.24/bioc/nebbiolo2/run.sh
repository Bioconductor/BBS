#!/bin/bash

. ./config.sh

. $BBS_HOME/utils/clean-before-run.sh

$BBS_PYTHON_CMD $BBS_HOME/BBS-run.py no-bin

# EXPERIMENT (nebbiolo2 only): the user-wide 'kill -9 -1' that used to end this
# script is disabled because it may also kill annotation/experiment builds that
# run as the same user at the same time. Instead, list the processes still
# running as this user so we can see whether any strays are left after a run
# and which build each one belongs to. Nothing is killed here.
echo "BBS> [stray-check] BBS-run.py finished at `date '+%Y-%m-%d %H:%M:%S'`"
sleep 60  # give normal shutdowns a minute to finish before listing
echo "BBS> [stray-check] `date '+%Y-%m-%d %H:%M:%S'` processes still running as $USER (kill is disabled)"
echo "BBS> [stray-check] format: PID PPID ELAPSED RSS_KB COMMAND | build=BBS_WORK_TOPDIR of the process | cwd=working directory"
pids=`ps -u "$USER" -o pid=`
for pid in $pids; do
    [ "$pid" = "$$" ] && continue
    # The process may have exited since ps ran, or may not be readable.
    [ -r /proc/$pid/environ ] || continue
    info=`ps -p $pid -o ppid=,etime=,rss=,args= 2>/dev/null` || continue
    build=`tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | sed -n 's/^BBS_WORK_TOPDIR=//p' | head -n 1`
    cwd=`readlink /proc/$pid/cwd 2>/dev/null`
    echo "BBS> [stray-check] $pid $info | build=${build:-unknown} | cwd=${cwd:-unknown}"
done
echo "BBS> [stray-check] done"
