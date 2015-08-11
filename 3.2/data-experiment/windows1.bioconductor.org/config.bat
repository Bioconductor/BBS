@rem =====================
@rem Settings for windows1.bioconductor.org
@rem =====================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=windows1.bioconductor.org
set BBS_USER=biocbuild
set BBS_RSAKEY=C:\biocbld\.BBS\id_rsa
set BBS_WORK_TOPDIR=C:\biocbld\bbs-3.2-data-experiment
set BBS_R_HOME=C:\biocbld\bbs-3.2-bioc\R
set BBS_NB_CPU=6

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch


@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
