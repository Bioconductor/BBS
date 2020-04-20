@rem ===================
@rem Settings for tokay1
@rem ===================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=tokay1
set BBS_USER=bioctesting
set BBS_RSAKEY=C:\Users\bioctesting\.BBS\id_rsa
set BBS_WORK_TOPDIR=C:\Users\bioctesting\bbs-3.12-bioc-testing
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=2
set BBS_CHECK_NB_CPU=3

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%


@rem The Shared settings above already set BBS_HOME to the value defined
@rem in BBS/nodes/tokay1/local-settings.bat. We need to override this value.
set BBS_HOME=C:\Users\bioctesting\BBS
