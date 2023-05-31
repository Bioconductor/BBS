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

# Fail if there are links to the builder's gfortran
so_path="$R_LIBS/$pkgname/libs"
if [ -d "$so_path" ]; then
    for arch in $TARGET_ARCHS; do
        arch_so_path="${so_path}${arch}"
        for so_file in $arch_so_path/*.so; do
            bad_shared_libraries=`otool -L "$so_file" | grep /opt/gfortran`
            if [ ! -z "$bad_shared_libraries" ]; then
                exit 1
            fi
        done
    done
fi
