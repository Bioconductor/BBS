@rem ======================
@rem Settings for palomino3
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=palomino3
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=F:\biocbuild\bbs-3.15-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=21
set BBS_BUILD_NB_CPU=18
set BBS_CHECK_NB_CPU=20

@rem set BBS_STAGE2_MODE=multiarch
@rem set BBS_STAGE4_MODE=multiarch
@rem set BBS_STAGE5_MODE=multiarch
set BBS_BUILD_TIMEOUT=4800
set BBS_CHECK_TIMEOUT=4800

@rem Central build node is nebbiolo1 at DFCI.
set BBS_CENTRAL_RHOST=nebbiolo1
set BBS_RSH_CMD=ssh -F /cygdrive/f/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://155.52.207.165
set BBS_PRODUCT_TRANSMISSION_MODE=asynchronous



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
