@rem ======================
@rem Settings for palomino8
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=palomino8
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=F:\biocbuild\bbs-3.20-bioc-longtests
set BBS_R_HOME=C:\Users\biocbuild\bbs-3.20-bioc\R

@rem palomino8 has 32 logical CPUs.
set BBS_NB_CPU=8

@rem Central build node is bbscentral2 on Jetstream2.
set BBS_CENTRAL_RHOST=bbscentral2
set BBS_RSH_CMD=ssh -F /cygdrive/f/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://149.165.154.78
set BBS_PRODUCT_TRANSMISSION_MODE=asynchronous



@rem Shared settings (by all Windows nodes).

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
