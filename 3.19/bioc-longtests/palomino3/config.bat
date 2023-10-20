@rem ===================
@rem Settings for palomino3
@rem ===================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=palomino3
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=F:\biocbuild\bbs-3.19-bioc-longtests
set BBS_R_HOME=F:\biocbuild\bbs-3.19-bioc\R
set BBS_NB_CPU=8

@rem Central build node is nebbiolo1 at DFCI.
set BBS_CENTRAL_RHOST=nebbiolo1
set BBS_RSH_CMD=ssh -F /cygdrive/f/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://155.52.207.165



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
