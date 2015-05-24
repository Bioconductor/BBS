#!/bin/bash
#
# Typical use:
#   ssh biocbuild@lamb2
#   cd ~/public_html/BBS/2.7/bioc/nodes/lamb2/buildsrc
#   ~/BBS/utils/extract-pkg-file-sizes.sh
#

ls -lhS *.tar.gz | sed -r "s/ +/\t/g" | cut -f 5,8

