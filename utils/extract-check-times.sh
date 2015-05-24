#!/bin/bash
#
# Typical use:
#   ssh biocbuild@lamb2
#   cd ~/public_html/BBS/2.7/bioc/nodes/liverpool/checksrc
#   ~/BBS/utils/extract-check-times.sh
#

grep 'EllapsedTime: ' *.checksrc-summary.dcf | sed -r "s/^(.*)\.checksrc-summary\.dcf:EllapsedTime: (.*) seconds/\2\t\1/" | sort -nr

