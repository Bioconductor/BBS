@rem ====================
@rem Settings for lemming
@rem ====================



set BBS_DEBUG=0

set BBS_NODE=lemming
set BBS_USER=biocbuild
set BBS_NB_CPU=4
set BBS_WORK_TOPDIR=D:\biocbld\bbs-2.2-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%

