@rem =====================
@rem Settings for moscato2
@rem =====================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=moscato2
set BBS_USER=biocbuild
set BBS_RSAKEY=E:\biocbld\.BBS\id_rsa
set BBS_WORK_TOPDIR=E:\biocbld\bbs-2.12-data-experiment
set BBS_R_HOME=E:\biocbld\bbs-2.12-bioc\R
set BBS_NB_CPU=13

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch


@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
