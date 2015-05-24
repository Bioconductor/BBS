@rem ===================
@rem Settings for gewurz
@rem ===================


set BBS_DEBUG=0

set BBS_NODE=gewurz
set BBS_USER=biocbuild
set BBS_NB_CPU=3
set BBS_WORK_TOPDIR=D:\biocbld\bbs-2.3-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R


@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
