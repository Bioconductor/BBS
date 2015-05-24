#!/bin/bash
# ========================
# Start a virtual X server
# ========================

pkill -9 Xsun
/usr/openwin/bin/Xvfb :0 -screen 0 800x600x16 &
xvfb_pid=$!
export DISPLAY=:0.0
