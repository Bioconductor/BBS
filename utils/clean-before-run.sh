#!/bin/bash

# Remove 00LOCK (just in case).
rm -rf "$BBS_R_HOME/library/00LOCK*" "$BBS_R_HOME/site-library/00LOCK*"

# Clean the tmp dir.
# Note: The trailing / in /tmp/ is required on Mac OS X!
find /tmp/ -depth -user $USER -mtime +1 -exec rm -rfv {} \; 2>/dev/null

