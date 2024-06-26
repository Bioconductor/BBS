@rem ======================
@rem Settings for palomino7
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=palomino7
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=F:\biocbuild\bbs-3.19-workflows
set BBS_R_HOME=F:\biocbuild\bbs-3.19-bioc\R

@rem palomino7 has 32 logical CPUs.
set BBS_NB_CPU=10
set BBS_BUILD_NB_CPU=8

@rem Central build node is bbscentral1 on Jetstream2.
set BBS_CENTRAL_RHOST=bbscentral1
set BBS_RSH_CMD=ssh -F /cygdrive/f/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://149.165.171.124
set BBS_PRODUCT_TRANSMISSION_MODE=asynchronous

@rem Source tarballs produced during STAGE3 won't be propagated
@rem so we don't need to push them to the central builder.
set DONT_PUSH_SRCPKGS=1



@rem Shared settings (by all Windows nodes).

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
