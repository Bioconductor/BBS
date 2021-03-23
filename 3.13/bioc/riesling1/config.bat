@rem ======================
@rem Settings for riesling1
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=riesling1
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=D:\biocbuild\bbs-3.13-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=36
set BBS_CHECK_NB_CPU=48

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch

@rem Central build node is nebbiolo1 at DFCI.
set BBS_CENTRAL_RHOST=nebbiolo1
set BBS_SSH_CONFIG_FILE=D:\\biocbuild\\.ssh\\config
set BBS_RSH_CMD=C:\cygwin\bin\ssh.exe -F %BBS_SSH_CONFIG_FILE%
set BBS_CENTRAL_ROOT_URL=http://155.52.207.165



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
