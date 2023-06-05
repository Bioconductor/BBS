#!/usr/bin/env bash
# ===================================
# Settings for kunpeng2 (Linux ARM64)
# ===================================

# Specific for openEuler START because some libraries are installed from source
export LIBSBML_CFLAGS=$(pkg-config --cflags ~/libsbml-from-git/lib/pkgconfig/libsbml.pc)
export LIBSBML_LIBS=$(pkg-config --libs ~/libsbml-from-git/lib/pkgconfig/libsbml.pc)
export UDUNITS2_INCLUDE="/home/biocbuild/libudunits-2/include"
export UDUNITS2_LIBS="/home/biocbuild/libudunits-2/lib"
export OPEN_BABEL_HOME="/home/biocbuild/openbabel-3.1.1"
export OPENBABEL_CFLAGS="-I$OPEN_BABEL_HOME/include/openbabel3 -L$OPEN_BABEL_HOME/lib"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib64:$UDUNITS2_LIBS:/home/biocbuild/libsbml-from-git/lib:$OPEN_BABEL_HOME/lib
export PATH=$PATH:/usr/lib64/openmpi/bin:/home/biocbuild/libudunits-2/bin:$HOME/.dotnet:$OPEN_BABEL_HOME/bin
# Settings specific for openEuler END

#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="kunpeng2"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.18-bioc"
export BBS_R_HOME="/home/biocbuild/R/R-4.3.0"
export R_LIBS="$BBS_R_HOME/site-library"
export BBS_NB_CPU=28         # 32 cores are available
export BBS_BUILD_NB_CPU=20   # 32 cores are available
export BBS_CHECK_NB_CPU=25   # 32 cores are available

export BBS_PRODUCT_TRANSMISSION_MODE="none"

# Central build node is nebbiolo2 at DFCI.
export BBS_CENTRAL_ROOT_URL="http://155.52.207.166"

# Source tarballs produced during STAGE3 won't be propagated so
# we don't need to make them available to the central builder.
export DONT_PUSH_SRCPKGS="1"

# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
