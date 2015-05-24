@rem ======================
@rem Settings for liverpool
@rem ======================


set BBS_DEBUG=0

set BBS_NODE=liverpool
set BBS_USER=biocbuild2
set BBS_RSAKEY=E:\biocbld\.BBS\id_rsa2
set BBS_WORK_TOPDIR=E:\biocbld\bbs-2.9-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=4

set RCYTOSCAPE_PORT_OVERRIDE=6000
set RCYTOSCAPE_HOST_OVERRIDE=wilson1


@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
