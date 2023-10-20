@rem ======================
@rem Settings for palomino3
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=palomino3
set BBS_USER=bioctesting
set BBS_WORK_TOPDIR=F:\bioctesting\bbs-3.19-bioc-testing
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=2
set BBS_CHECK_NB_CPU=3

@rem Central build node is nebbiolo1 at DFCI.
set BBS_CENTRAL_RHOST=nebbiolo1
set BBS_RSH_CMD=ssh -F /cygdrive/f/bioctesting/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://155.52.207.165
set BBS_PRODUCT_TRANSMISSION_MODE=asynchronous



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%


@rem The Shared settings above already set BBS_HOME to the value defined
@rem in BBS/nodes/palomino3/local-settings.bat. We need to override this value.
set BBS_HOME=F:\bioctesting\BBS
