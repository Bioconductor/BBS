@rem ===================
@rem Settings for gewurz
@rem ===================


set BBS_DEBUG=0

set BBS_NODE=gewurz
set BBS_USER=biocbuild
set BBS_RSAKEY=D:\biocbld\.BBS\id_rsa
set BBS_WORK_TOPDIR=D:\biocbld\bbs-2.6-data-experiment
set BBS_R_HOME=D:\biocbld\bbs-2.6-bioc\R
set BBS_NB_CPU=2


@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
