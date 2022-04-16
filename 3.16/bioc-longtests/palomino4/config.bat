@rem ===================
@rem Settings for palomino4
@rem ===================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=palomino4
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=C:\Users\biocbuild\bbs-3.16-bioc-longtests
set BBS_R_HOME=C:\Users\biocbuild\bbs-3.16-bioc\R
set BBS_NB_CPU=8

set BBS_STAGE4_MODE=multiarch

@rem Central build node is nebbiolo2 at DFCI.
set BBS_CENTRAL_RHOST=nebbiolo2
set BBS_RSH_CMD=ssh -F /cygdrive/c/Users/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://155.52.207.166



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
