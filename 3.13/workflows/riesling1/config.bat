@rem ======================
@rem Settings for riesling1
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=riesling1
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=D:\biocbuild\bbs-3.13-workflows
set BBS_R_HOME=D:\biocbuild\bbs-3.13-bioc\R
set BBS_NB_CPU=12

set BBS_STAGE2_MODE=multiarch

@rem Central build node is rex3 at BHW.
set BBS_CENTRAL_RHOST=155.52.173.35

@rem When used with StrictHostKeyChecking=no, ssh will automatically add new
@rem host keys to the user known hosts files (so it doesn't get stalled waiting
@rem for an answer when not run interactively).
set BBS_RSH_CMD=C:\cygwin\bin\ssh.exe -qi D:\biocbuild\.BBS\id_rsa -o StrictHostKeyChecking=no



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
