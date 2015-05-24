#!/bin/bash
# =======================================================
# Stop the virtual X server started by start-virtual-X.sh
# =======================================================

kill $xvfb_pid
pkill Xsun
