@rem ======================
@rem Settings for cyclonus
@rem ======================


set BBS_DEBUG=0

set BBS_NODE=cyclonus
set BBS_USER=biocbuild2
set BBS_RSAKEY=c:/packagebuilder/.packagebuilder.private_key.rsa
set BBS_WORK_TOPDIR=C:\biocbuild\bbs-2.9-bioc
set BBS_R_HOME=C:\biocbuild\R
set BBS_NB_CPU=4

set RCYTOSCAPE_PORT_OVERRIDE=6000
set RCYTOSCAPE_HOST_OVERRIDE=wilson1


@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
