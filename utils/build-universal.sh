#!/bin/bash
#
# Script for building a universal binary package from the source package (tarball).
# Typical use:
#
#   ./build-universal.sh affyio_1.5.8.tar.gz
#
# Note that this scripts does NOT check the source package!
#
# Author: Hervé Pagès <hpages.on.github@gmail.com>
# Last modified: 2007-08-11

INST_SCRIPT=`dirname "$0"`/macosx-inst-pkg.sh
MKTGZ_SCRIPT=`dirname "$0"`/macosx-make-tgz.sh

. $INST_SCRIPT

$MKTGZ_SCRIPT "$R_LIBS/$pkgname"
