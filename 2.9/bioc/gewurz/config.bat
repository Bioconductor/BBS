@rem ===================
@rem Settings for gewurz
@rem ===================


set BBS_DEBUG=0

set BBS_NODE=gewurz
set BBS_USER=biocbuild2
set BBS_RSAKEY=D:\biocbld\.BBS\id_rsa2
set BBS_WORK_TOPDIR=D:\biocbld\bbs-2.9-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=3

set RCYTOSCAPE_PORT_OVERRIDE=5000
set RCYTOSCAPE_HOST_OVERRIDE=wilson1


@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
