#!/usr/bin/env bash
# =========================================
# Local settings for kunpeng2 (openEuler Linux ARM64)
# =========================================


if [ -z "$BBS_HOME" ]; then
    export BBS_HOME="/home/biocbuild/BBS"
fi

export BBS_PYTHON_CMD="/usr/bin/python3"

export BBS_SSH_CMD="/usr/bin/ssh"
export BBS_RSYNC_CMD="/usr/bin/rsync"
export BBS_TAR_CMD="/usr/bin/tar"

# Needed only on a node capable of running STAGE1 (STAGE1 is supported on
# Linux only)
#export BBS_SVN_CMD="/usr/bin/svn"
export BBS_GIT_CMD="/usr/bin/git"
export BBS_CURL_CMD="/usr/bin/curl"


# We need these because some of the libraries/dependecies are installed from source
export LIBSBML_CFLAGS=$(pkg-config --cflags ~/libsbml-from-git/lib/pkgconfig/libsbml.pc)
export LIBSBML_LIBS=$(pkg-config --libs ~/libsbml-from-git/lib/pkgconfig/libsbml.pc)
export UDUNITS2_INCLUDE="/home/biocbuild/libudunits-2/include"
export UDUNITS2_LIBS="/home/biocbuild/libudunits-2/lib"
export OPEN_BABEL_HOME="/home/biocbuild/openbabel-3.1.1"
export OPENBABEL_CFLAGS="-I$OPEN_BABEL_HOME/include/openbabel3 -L$OPEN_BABEL_HOME/lib"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib64:$UDUNITS2_LIBS:/home/biocbuild/libsbml-from-git/lib:$OPEN_BABEL_HOME/lib
export PATH=$PATH:/usr/lib64/openmpi/bin:/home/biocbuild/libudunits-2/bin:$HOME/.dotnet:$OPEN_BABEL_HOME/bin
