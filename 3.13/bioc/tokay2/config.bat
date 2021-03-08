@rem ===================
@rem Settings for tokay2
@rem ===================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=tokay2
set BBS_USER=biocbuild
set BBS_RSAKEY=C:\Users\biocbuild\.BBS\id_rsa
set BBS_WORK_TOPDIR=C:\Users\biocbuild\bbs-3.13-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=16
set BBS_CHECK_NB_CPU=26

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch

@rem rex3 is not in the DNS so we use its IP address
set BBS_CENTRAL_RHOST=155.52.173.35
set BBS_MEAT0_RHOST=155.52.173.35
set BBS_GITLOG_RHOST=155.52.173.35



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
