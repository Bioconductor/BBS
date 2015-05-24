@rem ===================
@rem Settings for gewurz
@rem ===================


set BBS_DEBUG=0

set BBS_NODE=gewurz
set BBS_USER=biocbuild2
set BBS_RSAKEY=D:\biocbld\.BBS\id_rsa2
set BBS_WORK_TOPDIR=D:\biocbld\bbs-2.7-data-experiment
set BBS_R_HOME=D:\biocbld\bbs-2.7-bioc\R
set BBS_NB_CPU=2


@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
