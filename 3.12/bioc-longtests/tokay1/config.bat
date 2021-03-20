@rem ===================
@rem Settings for tokay1
@rem ===================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=tokay1
set BBS_USER=biocbuild
set BBS_RSAKEY=C:\Users\biocbuild\.BBS\id_rsa
set BBS_WORK_TOPDIR=C:\Users\biocbuild\bbs-3.12-bioc-longtests
set BBS_R_HOME=C:\Users\biocbuild\bbs-3.12-bioc\R
set BBS_NB_CPU=4

set BBS_STAGE4_MODE=multiarch

@rem We use malbec1 internal IP address (DMZ-IP)
set BBS_CENTRAL_RHOST=172.29.0.3
set BBS_MEAT0_RHOST=172.29.0.3
set BBS_GITLOG_RHOST=172.29.0.3



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
