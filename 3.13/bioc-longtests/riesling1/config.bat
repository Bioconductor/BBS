@rem ======================
@rem Settings for riesling1
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=riesling1
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=D:\biocbuild\bbs-3.13-bioc-longtests
set BBS_R_HOME=D:\biocbuild\bbs-3.13-bioc\R
set BBS_NB_CPU=10

set BBS_STAGE4_MODE=multiarch

@rem Central build node is malbec2 at RPCI. We use its internal IP
@rem address (DMZ-IP).
set BBS_CENTRAL_RHOST=malbec2
set BBS_RSH_CMD=ssh -F /cygdrive/d/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://172.29.0.4



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
