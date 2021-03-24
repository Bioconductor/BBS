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

@rem Central build node is nebbiolo1 at DFCI.
set BBS_CENTRAL_RHOST=nebbiolo1
set BBS_RSH_CMD=ssh -F /cygdrive/d/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://155.52.207.165

@rem Source tarballs produced during STAGE3 won't be propagated
@rem so we don't need to push them to the central builder.
set DONT_PUSH_SRCPKGS=1



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
