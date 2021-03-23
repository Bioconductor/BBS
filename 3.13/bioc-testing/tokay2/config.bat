@rem ===================
@rem Settings for tokay2
@rem ===================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=tokay2
set BBS_USER=bioctesting
set BBS_WORK_TOPDIR=C:\Users\bioctesting\bbs-3.13-bioc-testing
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=2
set BBS_CHECK_NB_CPU=3

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch

@rem Central build node is malbec2 at RPCI.
set BBS_CENTRAL_RHOST=malbec2
set BBS_RSH_CMD=ssh -F /cygdrive/c/Users/bioctesting/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://172.29.0.4



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%


@rem The Shared settings above already set BBS_HOME to the value defined
@rem in BBS/nodes/tokay2/local-settings.bat. We need to override this value.
set BBS_HOME=C:\Users\bioctesting\BBS
