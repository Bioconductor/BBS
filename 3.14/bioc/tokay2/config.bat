@rem ===================
@rem Settings for tokay2
@rem ===================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=tokay2
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=C:\Users\biocbuild\bbs-3.14-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=12
set BBS_CHECK_NB_CPU=16

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch

@rem Central build node is nebbiolo2 at DFCI.
set BBS_CENTRAL_RHOST=nebbiolo2
set BBS_RSH_CMD=ssh -F /cygdrive/d/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://155.52.207.166



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
