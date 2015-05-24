#!/bin/bash
#
# Typical use:
#   ssh biocbuild@lamb2
#   cd ~/public_html/BBS/2.7/bioc/nodes/liverpool/buildsrc
#   ~/BBS/utils/extract-build-times.sh
#

grep 'EllapsedTime: ' *.buildsrc-summary.dcf | sed -r "s/^(.*)\.buildsrc-summary\.dcf:EllapsedTime: (.*) seconds/\2\t\1/" | sort -nr

