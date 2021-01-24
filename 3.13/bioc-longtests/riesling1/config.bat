@rem ======================
@rem Settings for riesling1
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=riesling1
set BBS_USER=biocbuild
set BBS_RSAKEY=D:\biocbuild\.BBS\id_rsa
set BBS_WORK_TOPDIR=D:\biocbuild\bbs-3.13-bioc-longtests
set BBS_R_HOME=D:\biocbuild\bbs-3.13-bioc\R
set BBS_NB_CPU=10

set BBS_STAGE4_MODE=multiarch

set BBS_CENTRAL_RHOST=malbec2.bioconductor.org
set BBS_MEAT0_RHOST=malbec2.bioconductor.org
set BBS_GITLOG_RHOST=malbec2.bioconductor.org



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
